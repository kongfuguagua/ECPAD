package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/prometheus/client_golang/api"
	promv1 "github.com/prometheus/client_golang/api/prometheus/v1"
	"github.com/prometheus/common/model"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/component-base/logs"
	"k8s.io/klog/v2"
	"k8s.io/kubernetes/cmd/kube-scheduler/app"
	"k8s.io/kubernetes/pkg/scheduler/framework"
	frameworkruntime "k8s.io/kubernetes/pkg/scheduler/framework/runtime"
)

func main() {
	// rand.Seed(time.Now().UTC().UnixNano())

	command := app.NewSchedulerCommand(
		app.WithPlugin(Name, createNew),
	)

	logs.InitLogs()
	defer logs.FlushLogs()

	if err := command.Execute(); err != nil {
		_, _ = fmt.Fprintf(os.Stderr, "%v\n", err)
		os.Exit(1)
	}

}

const Name = "NetworkTraffic"

var _ framework.FilterPlugin = &NetworkTraffic{}
var _ framework.ScorePlugin = &NetworkTraffic{}

type NetworkTraffic struct {
	prometheus *PrometheusHandle
	handle     framework.Handle
}

type PrometheusHandle struct {
	deviceName string
	timeRange  time.Duration
	ip         string
	client     promv1.API
}

type NetworkTrafficArgs struct {
	IP         string `json:"ip"`
	DeviceName string `json:"deviceName"`
	TimeRange  int    `json:"timeRange"`
}

const (
	nodeMeasureQueryTemplate  = "sum_over_time(node_network_receive_bytes_total{device=\"%s\"}[%s]) * on(instance) group_left(nodename) (node_uname_info{instance=\"%s\"})"
	nodeMeasureQueryTemplate1 = "((node_memory_MemFree_bytes{instance=\"%s\"})+(node_memory_Cached_bytes{instance=\"%s\"})+(node_memory_Buffers_bytes{instance=\"%s\"}))/1024/1024/1024"
)

func (n *NetworkTraffic) Name() string {
	return Name
}

func (n *NetworkTraffic) Filter(ctx context.Context, state *framework.CycleState, p *corev1.Pod, nodeInfo *framework.NodeInfo) *framework.Status {
	nodeName := nodeInfo.Node().Name
	memFree, err := n.prometheus.GetGauge1(nodeName)
	klog.Infof("[NetworkTraffic]Node '%s' MemFree is: '%v'", nodeName, memFree.Value)
	if err != nil {
		return framework.NewStatus(framework.Error, fmt.Sprintf("error getting node memFree: %s", err))
	}
	if memFree.Value < 3.0 {
		klog.Infof("[NetworkTraffic]Node '%s' is unschedulable", nodeName)
		return framework.NewStatus(framework.Unschedulable, "该节点不可调度")
	}
	if memFree.Value >= 3.0 {
		klog.Infof("[NetworkTraffic]Node '%s' is schedulable", nodeName)
		return framework.NewStatus(framework.Success)
	}
	return nil
}

func (n *NetworkTraffic) Score(ctx context.Context, state *framework.CycleState, p *corev1.Pod, nodeName string) (int64, *framework.Status) {
	nodeBandwidth, err := n.prometheus.GetGauge(nodeName)
	if err != nil {
		return 0, framework.NewStatus(framework.Error, fmt.Sprintf("error getting node bandwidth: %s", err))
	}
	bandWidth := int64(nodeBandwidth.Value)
	klog.Infof("[NetworkTraffic] node '%s' bandwidth: %v", nodeName, bandWidth)
	return bandWidth, framework.NewStatus(framework.Success, "")
}

func (n *NetworkTraffic) ScoreExtensions() framework.ScoreExtensions {
	return n
}

func (n *NetworkTraffic) NormalizeScore(ctx context.Context, state *framework.CycleState, pod *corev1.Pod, scores framework.NodeScoreList) *framework.Status {
	var higherScore int64 = 0
	for _, node := range scores {
		if higherScore < node.Score {
			higherScore = node.Score
		}
	}

	klog.Infof("[NetworkTraffic] highest score: %v", higherScore)
	for i, node := range scores {
		klog.Infof("[NetworkTraffic] operation: %v - ( %v * 100 / %v)", framework.MaxNodeScore, node.Score, higherScore)
		scores[i].Score = framework.MaxNodeScore - (node.Score * 100 / higherScore)
		klog.Infof("[NetworkTraffic] node '%s' final score: %v", node, scores[i].Score)
	}

	klog.Infof("[NetworkTraffic] Nodes final score: %v", scores)
	return framework.NewStatus(framework.Success, "")
}

func createNew(ctx context.Context, plArgs runtime.Object, f framework.Handle) (framework.Plugin, error) {
	args := &NetworkTrafficArgs{}
	if err := frameworkruntime.DecodeInto(plArgs, args); err != nil {
		return nil, err
	}

	klog.Infof("[NetworkTraffic] args received. Device: %s; TimeRange: %d, Address: %s", args.DeviceName, args.TimeRange, args.IP)

	return &NetworkTraffic{
		handle:     f,
		prometheus: NewProme(args.IP, args.DeviceName, time.Second*time.Duration(args.TimeRange)),
	}, nil
}

func NewProme(ip, deviceName string, timeRace time.Duration) *PrometheusHandle {
	client, err := api.NewClient(api.Config{Address: ip})
	if err != nil {
		klog.Fatalf("[NetworkTraffic] FatalError creating prometheus client: %s", err.Error())
	}
	return &PrometheusHandle{
		deviceName: deviceName,
		ip:         ip,
		timeRange:  timeRace,
		client:     promv1.NewAPI(client),
	}
}

func (p *PrometheusHandle) GetGauge(node string) (*model.Sample, error) {
	value, err := p.query(fmt.Sprintf(nodeMeasureQueryTemplate, p.deviceName, p.timeRange, node))
	fmt.Println(fmt.Sprintf(nodeMeasureQueryTemplate, p.deviceName, p.timeRange, node))
	if err != nil {
		return nil, fmt.Errorf("[NetworkTraffic] Error querying prometheus: %w", err)
	}

	nodeMeasure := value.(model.Vector)
	if len(nodeMeasure) != 1 {
		return nil, fmt.Errorf("[NetworkTraffic] Invalid response, expected 1 value, got %d", len(nodeMeasure))
	}
	return nodeMeasure[0], nil
}

func (p *PrometheusHandle) GetGauge1(node string) (*model.Sample, error) {
	value, err := p.query(fmt.Sprintf(nodeMeasureQueryTemplate1, node, node, node))
	fmt.Println(fmt.Sprintf(nodeMeasureQueryTemplate1, node, node, node))
	if err != nil {
		return nil, fmt.Errorf("[NetworkTraffic] Error querying prometheus: %w", err)
	}

	nodeMeasure := value.(model.Vector)

	return nodeMeasure[0], nil
}

func (p *PrometheusHandle) query(promQL string) (model.Value, error) {
	// 通过promQL查询并返回结果
	results, warnings, err := p.client.Query(context.Background(), promQL, time.Now())
	if len(warnings) > 0 {
		klog.Warningf("[NetworkTraffic Plugin] Warnings: %v\n", warnings)
	}
	return results, err
}
