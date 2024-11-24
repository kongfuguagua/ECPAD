package main

import (
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gorilla/mux"
	"github.com/hashicorp/consul/api"
)

const service_name = "my-service"
const service_id = "my-service-id"

var service_address = "127.0.0.1"

const service_port = 8080

func main() {
	// 指定该服务是否进行注册
	noregister := flag.Bool("noregister", false, "do not register service to consul")
	// 指定consul服务器地址
	consulAddress := flag.String("consulip", "127.0.0.1:8500", "consul ip address")

	flag.Parse()

	// 获取本机的IPv4地址
	localIPv4, err := getLocalIPv4InSubnet("192.168.")
	if err != nil {
		log.Fatalf("Error getting local IPv4 address: %s", err)
	}
	service_address = localIPv4
	log.Printf("Local IPv4 address: %s", service_address)

	// 初始化 Consul 客户端
	consulClient, err := api.NewClient(&api.Config{
		Address: *consulAddress, // Consul 服务地址
	})
	if err != nil {
		log.Fatalf("Error initializing Consul client: %s", err)
	}

	// 构建路由
	r := mux.NewRouter()

	// 健康检查端点
	r.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Healthy")
	})

	// 服务端点
	r.HandleFunc("/service", func(w http.ResponseWriter, r *http.Request) {
		switch r.Method {
		case http.MethodGet:
			fmt.Fprintln(w, "Service is up and running")
		case http.MethodPost:
			body, err := io.ReadAll(r.Body)
			if err != nil {
				http.Error(w, "Failed to read request body", http.StatusBadRequest)
				return
			}
			defer r.Body.Close()

			// 这里是处理请求的核心部分
			response, err := calculateStringLengthAndRespond("service_name", body)
			if err != nil {
				http.Error(w, "Failed to process request", http.StatusInternalServerError)
				return
			}

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusOK)
			w.Write(response)
		default:
			http.Error(w, "Method Not Allowed", http.StatusMethodNotAllowed)
		}
	}).Methods("GET", "POST")

	// 启动 HTTP 服务器
	server := &http.Server{
		Handler:      r,
		Addr:         ":8080",
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
	}

	health_address := "http://" + service_address + ":" + fmt.Sprintf("%d", service_port) + "/health"

	// 注册服务到 Consul
	if !*noregister {
		err = consulClient.Agent().ServiceRegister(&api.AgentServiceRegistration{
			Name:    service_name,
			ID:      service_id,
			Address: service_address,
			Port:    service_port,
			Check: &api.AgentServiceCheck{
				HTTP:     health_address,
				Interval: "10s",
				Timeout:  "1s",
			},
		})
	}
	if err != nil {
		log.Fatalf("Error registering service: %s", err)
	}

	// 用于监听系统信号的通道
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

	// 开启一个goroutine等待信号
	go func() {
		sig := <-sigCh
		log.Printf("Received signal: %v, starting graceful shutdown", sig)

		if !*noregister {
			// 取消注册服务
			if deregErr := consulClient.Agent().ServiceDeregister("my-service-id"); deregErr != nil {
				log.Printf("Error deregistering service from Consul: %s", deregErr)
			} else {
				log.Println("Service successfully deregistered from Consul.")
			}
		}

		// 尝试优雅关闭HTTP服务器
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		if err := server.Shutdown(ctx); err != nil {
			log.Printf("HTTP server shutdown error: %v", err)
		}

		os.Exit(0)
	}()

	// 启动服务
	log.Println("Starting HTTP server...")
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("ListenAndServe() error: %s", err)
	}
}

// 示例运行: go run . --consulip=192.168.3.100:8500
// 示例请求: curl -X POST http://IP:Port/service -d "hello, world"

// 此时的服务只能对请求做出回应，下一步需要考虑请求数据的格式，根据格式进行解析处理
// 进一步考虑多个微服务之间的转发，回应是OK，实际数据被转发到了别的服务进行处理
// 容器化运行之后的IP地址变化，需要改变一下utils里面的函数
