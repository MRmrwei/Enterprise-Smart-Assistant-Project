// Code scaffolded by goctl. Safe to edit.
// goctl 1.10.1

package main

import (
	"flag"
	"fmt"
	"gateway/internal/config"
	"github.com/zeromicro/go-zero/core/conf"
	"github.com/zeromicro/go-zero/gateway"
)

var configFile = flag.String("f", "etc/gateway-api.yaml", "the config file")

func main() {
	flag.Parse()
	var c config.Config // 或使用你自定义的 config.Config
	conf.MustLoad(*configFile, &c)
	gw := gateway.MustNewServer(c.GatewayConf)
	defer gw.Stop()

	fmt.Printf("Starting gateway at %s:%d...\n", c.Host, c.Port)
	gw.Start()
}
