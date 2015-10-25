var CFD = "不限";
var CSD = "不限";
var ShowT = 1;
var CFData = [];
var CSData = [];
var CAData = '';
var CLIST = '美食-1$本帮江浙菜-11,川菜-12,粤菜-13,湘菜-14,贵州菜-15,东北菜-16,台湾菜-17,新疆/清真菜-18,西北菜-19,素菜-20,火锅-21,自助餐-22,小吃快餐-23,日本-24,韩国料理-25,东南亚菜-26,西餐-27,面包甜点-28,其他-29#休闲娱乐-2$密室-30,咖啡厅-31,酒吧-32,茶馆-33,KTV-34,电影院-35,门票-36,足疗按摩-39,洗浴-40,游乐游艺-41,桌球-42,桌面游戏-43,其他-45#购物-3$综合商场-46,食品茶酒-47,服饰鞋包-48,珠宝饰品-49,化妆品-50,运动户外-51,亲子购物-52,品牌折扣店-53,数码家电-54,家居建材-55,特色集市-56,书店-57,花店-58,眼镜店-59,超市/便利店-60,药店-61,其他-62#丽人-4$美发-63,美容/SPA-64,化妆品-65,瘦身纤体-66,美甲-67,瑜伽-68,舞蹈-69,个性写真-70,整形-71,齿科-72,其他-73#旅游-5$观光游-74,景区-75,采摘园-76,旅行社-77,度假村-78,温泉-79#运动健身-7$游泳馆-92,羽毛球馆-93,健身中心-94,瑜伽-95,舞蹈-96,篮球场-97,网球场-98,足球场-99,高尔夫场-100,保龄球馆-101,桌球馆-102,乒乓球馆-103,武术场馆-104,体育场馆-105,其他-106#酒店-8$五星级酒店-107,四星级酒店-108,三星级酒店-109,经济型酒店-110,公寓式酒店-111,精品酒店-112,青年旅舍-113,度假村-114,其他-115#生活服务-10$培训-126,室内装潢-127,婚纱摄影-128,齿科-129,快照/冲印-130,家政-131,银行-132,学校-133';
function CS() {
    if (ShowT)CLIST = CFD + "$" + CSD + "#" + CLIST;
    CAData = CLIST.split("#");
    for (var i = 0; i < CAData.length; i++) {
        parts = CAData[i].split("$");
        CFData[i] = parts[0];
        CSData[i] = parts[1].split(",")
    }
    var self = this;
    this.SelF = document.getElementById('industry_1');
    this.SelS = document.getElementById('industry_2');
    this.DefF = this.SelF.getAttribute('value');
    this.DefS = this.SelS.getAttribute('value');
    this.SelF.CS = this;
    this.SelS.CS = this;
    this.SelF.onchange = function () {
        CS.SetS(self)
    };
    CS.SetF(this)
};
CS.SetF = function (self) {
    for (var i = 0; i < CFData.length; i++) {
        var title, value;
        title = CFData[i].split("-")[0];
        value = CFData[i].split("-")[0];
        if (title == CFD) {
            value = ""
        }
        self.SelF.options.add(new Option(title, value));
        if (self.DefF == value) {
            self.SelF[i].selected = true
        }
    }
    CS.SetS(self)
};
CS.SetS = function (self) {
    var fi = self.SelF.selectedIndex;
    var slist = CSData[fi];
    self.SelS.length = 0;
    if (self.SelF.value != "" && ShowT) {
        self.SelS.options.add(new Option(CSD, ""))
    }
    for (var i = 0; i < slist.length; i++) {
        var title, value;
        title = slist[i].split("-")[0];
        value = slist[i].split("-")[0];
        if (title == CSD) {
            value = ""
        }
        self.SelS.options.add(new Option(title, value));
        if (self.DefS == value) {
            self.SelS[self.SelF.value != "" ? i + 1 : i].selected = true
        }
    }
};
$(function () {
    CS();
});