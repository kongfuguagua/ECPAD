#include <ESP8266WiFi.h>             // esp8266库
#include <MySQL_Connection.h>    // Arduino连接Mysql的库
#include <MySQL_Cursor.h>

IPAddress server_addr(192,168,3,37);   // 安装Mysql的电脑的IP地址
char user[] = "arduino_user";              // Mysql的用户名
char password[] = "123456";        // 登陆Mysql的密码

// Mysql中添加一条数据的命令
// arduino_test，test1：刚才创建的数据和表
char INSERT_SQL[] = "INSERT INTO  shine.sensors(id,time,num,type) VALUES ('%d','%s','%d','%s')";

const char* ssid     = "kczx-zhonglou";                // 需要连接到的WiFi名
const char* pass = "abcd1234";             // 连接的WiFi密码

WiFiClient client;                 // 声明一个Mysql客户端，在lianjieMysql中使用
MySQL_Connection conn((Client *)&client);

void wificonnect(){
  WiFi.mode(WIFI_STA);                          // 设置Wifi工作模式为STA,默认为AP+STA模式
  WiFi.begin(ssid, pass);                   // 通过wifi名和密码连接到Wifi
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

void readAndRecordData(){
    char buff[256]; // 定义存储传感器数据的数组
    char time[20]="2024-03-29";
    char type[5]="pv"; // 修改为3，保证字符串结尾的\0也被包含
    sprintf(buff,INSERT_SQL,2,time,200,type); // 将id、time、num和type数据放入SQL中
    MySQL_Cursor *cursor = new MySQL_Cursor(&conn); // 创建一个Mysql实例
    cursor->execute(buff); // 将采集到的数据插入数据库中
    delete cursor; // 删除mysql实例为下次采集作准备
    Serial.println("writing");
}

void setup()
{
  Serial.begin(9600);
  wificonnect();

  Serial.print("Connecting to SQL...  ");
  if (conn.connect(server_addr, 3306, user, password))         // 连接数据库
    Serial.println("OK.");   
  else
    Serial.println("FAILED.");
}

void loop()
{
  readAndRecordData();        
  delay(5000);
}
