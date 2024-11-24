// 该服务的功能是将所有的 MQTT 消息存储到 Redis 中
package main

import (
	"context"
	// "flag"
	"fmt"
	"sync"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/go-redis/redis/v8"
	"github.com/hashicorp/consul/api"
)

var ctx = context.Background()
var rdb *redis.Client

// var redisAddress, redisPasswd, mqttAddress, mqttUsername, mqttPassword *string
var mqttAddress, redisAddress string

func main() {
	mqttAddress = getIpPortFromConsul("iiip-mqttbroker001-utils")
	redisAddress = getIpPortFromConsul("iiip-redis-core")
	// 从命令行参数获取 Redis 和 MQTT 服务器地址
	// redisAddress = flag.String("redisip", "127.0.0.1:6379", "Redis server address")
	// redisPasswd = flag.String("redispw", "", "Redis server password")
	// //noRedis := flag.Bool("noredis", false, "Don't use Redis")
	// mqttAddress = flag.String("mqttip", "127.0.0.1:1883", "MQTT server address")
	// mqttUsername = flag.String("mqttuser", "", "MQTT username")
	// mqttPassword = flag.String("mqttpw", "", "MQTT password")

	// flag.Parse()

	// 创建 Redis 客户端连接
	// rdb := redis.NewClient(&redis.Options{
	// 	Addr:     *redisAddress, // Redis服务器地址
	// 	Password: *redisPasswd,  // 如果设置了密码，需要在这里填写
	// 	DB:       0,             // 默认数据库编号
	// })

	setupRedis()

	// MQTT 连接选项
	// opts := mqtt.NewClientOptions().
	// 	AddBroker(*mqttAddress).
	// 	SetClientID("go_mqtt_to_redis").
	// 	SetUsername(*mqttUsername).
	// 	SetPassword(*mqttPassword).
	// 	SetAutoReconnect(true).                   // 开启自动重连
	// 	SetConnectRetry(true).                    // 开启重连尝试
	// 	SetConnectRetryInterval(5 * time.Second). // 设置重连间隔
	// 	SetOnConnectHandler(onConnect)

	opts := mqtt.NewClientOptions().
		AddBroker(mqttAddress).
		SetClientID("go_mqtt_to_redis").
		SetAutoReconnect(true).                   // 开启自动重连
		SetConnectRetry(true).                    // 开启重连尝试
		SetConnectRetryInterval(5 * time.Second). // 设置重连间隔
		SetOnConnectHandler(onConnect)

	// 创建 MQTT 客户端
	mqttClient := mqtt.NewClient(opts)

	// MQTT 连接
	if token := mqttClient.Connect(); token.Wait() && token.Error() != nil {
		fmt.Println("Error connecting to MQTT server:", token.Error())
	}

	// 订阅 MQTT 主题
	wait := sync.WaitGroup{}
	wait.Add(1)
	// token := mqttClient.Subscribe("mqttv1/#", 0, func(client mqtt.Client, msg mqtt.Message) {
	// 	// 将消息存储到 Redis 中
	// 	err := storeMessageToRedis(msg, rdb)
	// 	// err := rdb.Publish(ctx, msg.Topic(), msg.Payload()).Err()
	// 	if err != nil {
	// 		fmt.Println("Error set to Redis:", err)
	// 		if isRedisError(err) {
	// 			setupRedis()
	// 			time.Sleep(5 * time.Second)
	// 		}
	// 	}
	// })
	// token.Wait()

	wait.Wait()
	// 等待信号停止
	// select {}
}

func getIpPortFromConsul(servicename string) string {
	// 创建 Consul 客户端配置
	config := api.DefaultConfig()
	config.Address = "192.168.3.200:31995" // 替换为你的 Consul 地址和端口

	// 创建 Consul 客户端
	client, err := api.NewClient(config)
	if err != nil {
		panic(err)
	}

	// 查询服务的健康实例
	services, _, err := client.Health().Service(servicename, "", true, nil)
	if err != nil {
		panic(err)
	}

	// 提取服务的地址和端口
	var ipstring string
	for _, service := range services {
		ipstring = service.Service.Address + ":" + fmt.Sprintf("%d", service.Service.Port)
		// fmt.Printf(ipstring)
		break
	}
	return ipstring
}

func setupRedis() {
	redisAddress = getIpPortFromConsul("iiip-redis-core")
	rdb = redis.NewClient(&redis.Options{
		Addr: redisAddress,
		// Password: *redisPasswd,
		Password: "",
		DB:       0,
	})
	fmt.Println("Connected to Redis Server")
}
func onConnect(client mqtt.Client) {
	// 连接成功后的回调函数，掉线之后无法转发，需要重新设置订阅才可以
	fmt.Println("Connected to MQTT Broker")
	// 订阅 MQTT 主题
	token := client.Subscribe("mqttv1/#", 0, func(client mqtt.Client, msg mqtt.Message) {
		// 将消息存储到 Redis 中
		err := storeMessageToRedis(msg, rdb)
		if err != nil {
			fmt.Println("Error set to Redis:", err)
			if isRedisError(err) {
				setupRedis()
				time.Sleep(5 * time.Second)
			}
		}
	})
	token.Wait()
	if token.Error() != nil {
		fmt.Println("Error subscribing to topic:", token.Error())
	} else {
		fmt.Println("Subscribed to topic: mqttv1/#")
	}
}
func storeMessageToRedis(msg mqtt.Message, rdb *redis.Client) error {
	redis_key := msg.Topic()[7:]
	time_stamp := time.Now().Unix()
	redis_value := msg.Payload()

	return rdb.ZAdd(ctx, redis_key, &redis.Z{Score: float64(time_stamp), Member: redis_value}).Err()
}
func isRedisError(err error) bool {
	return err == redis.Nil || err.Error() == "redis: client is offline or not initialized"
}

// TODO：后续可以考虑服务运行着，然后通过外部的请求来设置mqtt的地址，这样就可以动态的修改mqtt的地址
// TODO：代码优化，拆分成通用的服务形式
