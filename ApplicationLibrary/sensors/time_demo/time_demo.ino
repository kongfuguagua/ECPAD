#include <WiFi.h>

const char* ssid     = "kczx-zhonglou";                // 需要连接到的WiFi名
const char* password = "abcd1234";             // 连接的WiFi密码

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

void setup()
{
    Serial.begin(115200);
    Serial.println();

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi connected!");

    // 从网络时间服务器上获取并设置时间
    // 获取成功后芯片会使用RTC时钟保持时间的更新
    configTime(gmtOffset_sec, 0, ntpServer);
    printLocalTime();
}

void loop()
{
    delay(1000);
    printLocalTime();
}
