package main

// 查找指定名称的微服务并发送测试数据

import (
	// "bytes"
	// "encoding/json"
	"flag"
	"fmt"
	"github.com/hashicorp/consul/api"
	"io"
	"log"
	"net/http"
	"strconv"
	"strings"
)

func main() {
	// 指定consul服务器地址
	consulAddress := flag.String("consulip", "192.168.3.100:8500", "consul ip address")

	flag.Parse()

	// 获取微服务地址
	service_addresses := get_service_address(*consulAddress, "my-service")
	service_address := service_addresses[0]

	// 发送测试数据
	data := "hello world"
	assemble_request(service_address, data)

}

// 不进行健康检查直接返回微服务
// func catalog_method(consulClient *api.Client) {
// 	catalogClient := consulClient.Catalog()
// 	services, _, err := catalogClient.Service("my-service", "", nil)
// 	if err != nil {
// 		log.Fatal(err)
// 	}
// 	for _, service := range services {
// 		log.Printf("Service: %s, Address: %s, Port: %d", service.ServiceName, service.ServiceAddress, service.ServicePort)
// 	}
// }

func assemble_request(service_address string, data string) {
	request_url := "http://" + service_address + "/service"

	// 将数据编码为JSON
	// payloadBytes, err := json.Marshal(data)
	// if err != nil {
	// 	log.Fatalf("Error encoding payload: %v", err)
	// }
	// payloadBody := bytes.NewReader(payloadBytes)
	payloadBody := strings.NewReader(data)

	// 创建请求
	req, err := http.NewRequest("POST", request_url, payloadBody)
	if err != nil {
		log.Fatalf("Error creating request: %v", err)
	}

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Fatalf("Error sending POST request: %v", err)
	}
	defer resp.Body.Close()

	// 处理响应
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Error reading response body: %v", err)
	}
	fmt.Printf("Response body: %s\n", respBody)
}
func get_service_address(consulAddress string, service_name string) []string {
	// 初始化 Consul 客户端
	consulClient, err := api.NewClient(&api.Config{
		Address: consulAddress, // Consul 服务地址
	})
	if err != nil {
		log.Fatalf("Error initializing Consul client: %s", err)
	}

	// catalog_method(consulClient)
	service_addresses := health_method(consulClient, service_name)
	// for _, address := range service_address {
	// 	log.Print(address)
	// }

	return service_addresses
}

// 健康检查，所有健康的微服务的地址会被返回
func health_method(consulClient *api.Client, service_name string) []string {
	var service_address []string

	healthClient := consulClient.Health()
	checks, _, err := healthClient.Service(service_name, "", true, nil)
	if err != nil {
		log.Fatal(err)
	}
	if len(checks) == 0 {
		log.Fatal("No healthy service found")
	}
	for _, check := range checks {
		node := check.Node
		service := check.Service
		log.Printf("Service: %s, Node: %s, Address: %s, Port: %d, Status: %s", service.Service, node.Node, service.Address, service.Port, check.Checks[0].Status)
		service_address = append(service_address, service.Address+":"+strconv.Itoa(service.Port))
	}
	return service_address
}
