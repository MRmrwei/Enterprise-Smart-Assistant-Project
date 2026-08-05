package config

import (
	"github.com/zeromicro/go-zero/gateway"
	"github.com/zeromicro/go-zero/zrpc"
)

type (
	Config struct {
		gateway.GatewayConf
		AgentAddr      []AgentAddr
		AgentRpcConfig zrpc.RpcClientConf
		AuthConfig     AuthConfig
	}
	AuthConfig struct {
		AccessSecret  string
		AccessExpire  int
		RefreshSecret string
		RefreshExpire int
	}

	AgentAddr struct {
		Name string
		Host string
		Path string
	}
)
