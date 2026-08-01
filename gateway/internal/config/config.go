package config

import (
	"github.com/zeromicro/go-zero/gateway"
	"github.com/zeromicro/go-zero/zrpc"
)

type Config struct {
	gateway.GatewayConf
	AgentRpcConfig zrpc.RpcClientConf
	AuthConfig     AuthConfig
}

type AuthConfig struct {
	AccessSecret  string
	AccessExpire  int
	RefreshSecret string
	RefreshExpire int
}
