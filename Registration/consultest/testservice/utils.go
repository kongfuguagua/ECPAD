package main

import (
	"fmt"
	"net"
	"strings"
)

// 获取本机属于192.168子网的IPv4地址
func getLocalIPv4InSubnet(subnet string) (string, error) {
	ifaces, err := net.Interfaces()
	if err != nil {
		return "", err
	}

	for _, iface := range ifaces {
		// 检查接口是否启用
		if iface.Flags&net.FlagUp == 0 {
			continue // 接口未启用，跳过
		}

		// 检查接口是否为回环接口
		if iface.Flags&net.FlagLoopback != 0 {
			continue // 接口为回环接口，跳过
		}

		addrs, err := iface.Addrs()
		if err != nil {
			return "", err
		}

		for _, addr := range addrs {
			var ip net.IP
			switch v := addr.(type) {
			case *net.IPNet:
				ip = v.IP
			case *net.IPAddr:
				ip = v.IP
			}

			// 检查是否为IPv4地址且位于指定子网
			if ip.To4() != nil && strings.HasPrefix(ip.String(), subnet) {
				return ip.String(), nil // 返回找到的符合子网的IPv4地址
			}
		}
	}

	return "", fmt.Errorf("no available IPv4 address in the %s subnet found", subnet)
}
