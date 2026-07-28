package config

import (
	"github.com/zeromicro/go-zero/gateway"
	"github.com/zeromicro/go-zero/zrpc"
)

type Config struct {
	gateway.GatewayConf
	AgentRpcConfig zrpc.RpcClientConf
	Auth           struct {
		AccessSecret string
		AccessExpire int64
	}
}
