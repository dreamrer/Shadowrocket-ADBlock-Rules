# Shadowrocket-ADBlock-Rules
----------------------------------------

## 黑名单过滤 + 广告

黑名单中包含了境外网站中无法访问的那些，对不确定的网站则默认直连。

- 代理：被墙的网站（GFWList）
- 直连：正常的网站
- 包含广告过滤

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_banlist_ad.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_top500_banlist_ad.png)

## 白名单过滤 + 广告

白名单中包含了境外网站中可以访问的那些，对不确定的网站则默认代理。

- 直连：top500 网站中可直连的境外网站、中国网站
- 代理：默认代理其余的所有境外网站
- 包含广告过滤

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_whitelist_ad.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_top500_whitelist_ad.png)


## 黑名单过滤

现在很多浏览器都自带了广告过滤功能，而广告过滤的规则其实较为臃肿，如果你不需要全局地过滤 App 内置广告和视频广告，可以选择这个不带广告过滤的版本。

- 代理：被墙的网站（GFWList）
- 直连：正常的网站
- 不包含广告过滤

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_banlist.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_top500_banlist.png)


## 白名单过滤

现在很多浏览器都自带了广告过滤功能，而广告过滤的规则其实较为臃肿，如果你不需要全局地过滤 App 内置广告和视频广告，可以选择这个不带广告过滤的版本。

- 直连：top500 网站中可直连的境外网站、中国网站
- 代理：默认代理其余的所有境外网站
- 不包含广告过滤

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_whitelist.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_top500_whitelist.png)


## 国内外划分 + 广告

国内外划分，对中国网站直连，外国网站代理。包含广告过滤。国外网站总是走代理，对于某些港澳台网站，速度反而会比直连更快。

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip_ad.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_cnip_ad.png)


## 国内外划分

国内外划分，对中国网站直连，外国网站代理。不包含广告过滤。国外网站总是走代理，对于某些港澳台网站，速度反而会比直连更快。

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_cnip.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_cnip.png)


## 直连去广告

如果你想将 SR 作为 iOS 全局去广告工具，这个规则会对你有所帮助。

- 直连：所有请求
- 包含广告过滤

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_direct_banad.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_direct_banad.png)


## 代理去广告

如果你想将 SR 作为 iOS 全局去广告 + 全局翻墙工具，这个规则会对你有所帮助。

- 直连：局域网请求
- 代理：其余所有请求
- 包含广告过滤

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_proxy_banad.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_proxy_banad.png)


## 回国规则

提供给海外华侨使用，可以回到墙内，享受国内的一些互联网服务。

- 直连：国外网站
- 代理：中国网站
- 不包含广告过滤

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_backcn.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_backcn.png)


## 回国规则 + 广告

提供给海外华侨使用，可以回到墙内，享受国内的一些互联网服务。

- 直连：国外网站
- 代理：中国网站
- 包含广告过滤

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_backcn_ad.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_backcn_ad.png)


## 仅去广告规则

仅包含去广告规则，不包含代理/直连规则。用于与其他规则联用。

- 仅包含去广告规则，不包含代理/直连规则。无任何其他配置。

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_ad_only.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/sr_ad_only.png)


----------------------------------------

以下规则基于 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 生成： 

## 懒人配置

不折腾，开箱即用。

- 配置简洁
- 规则覆盖范围广
- 国内外常用app单独分流

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/lazy.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/lazy.png)


## 懒人配置-含策略组

不折腾，开箱即用。下载规则后可在 i -> 代理分组 中自行配置。

- 配置简洁
- 规则覆盖范围广
- 国内外常用app单独分流
- 添加自动切换延迟最低节点类型
- 通过「代理分组」灵活调整流媒体分流策略

规则地址：<https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/lazy_group.conf>

![二维码](https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/figure/lazy_group.png)
