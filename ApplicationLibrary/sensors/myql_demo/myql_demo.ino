#include <WiFi.h>             // esp8266库
#include <MySQL_Connection.h>    // Arduino连接Mysql的库
#include <MySQL_Cursor.h>
#include <Wire.h>

//BH1750
#define ADDRESS_BH1750FVI 0x23  //ADDR="L" for this module
#define ONE_TIME_H_RESOLUTION_MODE 0x20
//One Time H-Resolution Mode:
//Resolution = 1 lux
//Measurement time (max.) = 180ms
//Power down after each measurement
byte highByte = 0;
byte lowByte = 0;
unsigned int sensorOut = 0;
unsigned int illuminance = 0;

void Getshine(){
   Wire.beginTransmission(ADDRESS_BH1750FVI); //"notify" the matching device
   Wire.write(ONE_TIME_H_RESOLUTION_MODE);   //set operation mode
   Wire.endTransmission();
   delay(180);
   Wire.requestFrom(ADDRESS_BH1750FVI, 2); //ask Arduino to read back 2 bytes from the sensor
   highByte = Wire.read(); // get the high byte
   lowByte = Wire.read(); // get the low byte
   sensorOut = (highByte<<8)|lowByte;
   illuminance = sensorOut/1.2;
}

//time
const char *ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 8 * 3600;// Beijing: UTC +8  -- 获取东八区时间(默认以英国格林威治天文台所在地的本初子午线为基准线的)
char timeBuffer[50]="";
void printLocalTime()
{
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo))
    {
        Serial.println("Failed to obtain time");
        return;
    }
    strftime(timeBuffer, sizeof(timeBuffer), "%F %T %A", &timeinfo); // 使用strftime格式化时间信息
    Serial.println(timeBuffer); // 打印格式化后的时间信息
}

//WIFI
const char* ssid     = "kczx-zhonglou";                // 需要连接到的WiFi名
const char* pass = "abcd1234";             // 连接的WiFi密码

void wificonnect(){
  Wire.begin();                                 //开启传感器io口
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


//Mysql
IPAddress server_addr(192,168,3,37);   // 安装Mysql的电脑的IP地址
char user[] = "arduino_user";              // Mysql的用户名
char password[] = "123456";        // 登陆Mysql的密码

// Mysql中添加一条数据的命令
// shine，sensors：刚才创建的数据和表
char INSERT_SQL[] = "INSERT INTO  shine.sensors(id,time,num,type) VALUES ('%d','%s','%d','%s')";

WiFiClient client;                 // 声明一个Mysql客户端，在lianjieMysql中使用
MySQL_Connection conn((Client *)&client);

char buff[512]; // 定义存储传感器数据的数组

char type[5]="pv"; 
unsigned int id=1;

void RecordData(){
    sprintf(buff,INSERT_SQL,id,timeBuffer,illuminance,type); // 将id、time、num和type数据放入SQL中
    MySQL_Cursor *cursor = new MySQL_Cursor(&conn); // 创建一个Mysql实例
    cursor->execute(buff); // 将采集到的数据插入数据库中
    delete cursor; // 删除mysql实例为下次采集作准备
    Serial.println("writing");
}

void setup()
{
  Serial.begin(9600);
  wificonnect();
  configTime(gmtOffset_sec, 0, ntpServer);      //配置时间传感器
  Serial.print("Connecting to SQL...  ");
  if (conn.connect(server_addr, 3306, user, password))         // 连接数据库
    Serial.println("OK.");   
  else
    Serial.println("FAILED.");
  
}

void loop()
{
  printLocalTime();
  Getshine();
  RecordData();        
  //  delay(1000);
  delay(1000*10*60); //10min写一次
}
