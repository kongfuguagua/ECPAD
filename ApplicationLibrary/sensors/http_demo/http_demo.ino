#include <ESP8266WiFi.h>                        // 本程序使用ESP8266WiFi库

/* 1. 设置Wifi接入信息 */
const char* ssid     = "kczx-zhonglou";                // 需要连接到的WiFi名
const char* password = "abcd1234";             // 连接的WiFi密码
#define host "www.baidu.com"
const int httpPort = 80;
/* 2. 开启wifi连接，连接成功后打印IP地址 */
void wificonnect(){
  WiFi.mode(WIFI_STA);                          // 设置Wifi工作模式为STA,默认为AP+STA模式
  WiFi.begin(ssid, password);                   // 通过wifi名和密码连接到Wifi
  Serial.print("\r\nConnecting to ");           // 串口监视器输出网络连接信息
  Serial.print(ssid); Serial.println(" ...");   // 显示NodeMCU正在尝试WiFi连接
  int i = 0;                                    // 检查WiFi是否连接成功
  while (WiFi.status() != WL_CONNECTED)         // WiFi.status()函数的返回值是由NodeMCU的WiFi连接状态所决定的。 
  {                                             // 如果WiFi连接成功则返回值为WL_CONNECTED
    delay(1000);                                // 此处通过While循环让NodeMCU每隔一秒钟检查一次WiFi.status()函数返回值
    Serial.print("waiting for ");                          
    Serial.print(i++); Serial.println("s...");       
  }                                             
  Serial.println("");                           // WiFi连接成功后
  Serial.println("WiFi connected!");            // NodeMCU将通过串口监视器输出"连接成功"信息。
  Serial.print("IP address: ");                 // 同时还将输出NodeMCU的IP地址。这一功能是通过调用
  Serial.println(WiFi.localIP());               // WiFi.localIP()函数来实现的。该函数的返回值即NodeMCU的IP地址。
}

void setup() {
  /* 1. 初始化串口通讯波特率为115200*/
  Serial.begin(115200);
  wificonnect();

}

void loop() {
  /* 1. 新建一个WiFiClient对象，即一个Wifi客户端 */
  WiFiClient tcpClient;

  /* 2. 创建一个用于发送Http请求的字符串*/
  String httpGetString = String("GET /") + " HTTP/1.1\r\n" +
                        "Host: " + host + "\r\n" +
                        "Connection: close\r\n" +
                        "\r\n";

  /* 3. 通过connect函数连接到网络服务器，连接成功后发送GET请求，连接失败则输出“连接失败”信息*/
  Serial.print("Connecting to "); Serial.println(host); 
  if(tcpClient.connect(host, httpPort))
  {
    Serial.print("Connected to "); Serial.print(host); Serial.println(" Success!"); 

    /* 1) 向服务器发送HTTP GET请求 */
    tcpClient.print(httpGetString);

    /* 2) 等待服务器返回消息，成功返回消息后打印出来 */
    Serial.println("\r\nWeb Server Response:");    
    while(tcpClient.connected() || tcpClient.available())
    {
      if(tcpClient.available())
      {
        String line = tcpClient.readStringUntil('\n');
        Serial.println(line);  
      }
    }

    /* 3) 收到消息后断开和服务器的连接 */
    tcpClient.stop();
    Serial.print("Disconnected from "); Serial.println(host);
  }
  else
  {
    Serial.println(" connection failed!");
    tcpClient.stop();
  }

  /* LED闪烁 */
  pinMode(2, OUTPUT);
  while(1){
    digitalWrite(2, LOW);
    delay(300);
    digitalWrite(2, HIGH);
    delay(300);  
  }
}

