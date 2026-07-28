// Code scaffolded by goctl. Safe to edit.
// goctl 1.10.1

package svc

import (
	"gateway/internal/config"
	"gateway/internal/svc/app"
	"gateway/pb"
	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/zrpc"
)

type ServiceContext struct {
	config         config.Config
	agentRpcClient pb.AiClient
}

func (s *ServiceContext) Config() config.Config {
	return s.config
}

func (s *ServiceContext) Client() pb.AiClient {
	return s.agentRpcClient
}

func NewServiceContext(c config.Config) app.Application {
	return &ServiceContext{
		config:         c,
		agentRpcClient: newAgentRpcClient(c.AgentRpcConfig),
	}
}

func newAgentRpcClient(c zrpc.RpcClientConf) pb.AiClient {
	conn, err := zrpc.NewClient(c)
	if err != nil {
		logx.Error("ai.rpc 连接失败！原因", err.Error())
	}
	return pb.NewAiClient(conn.Conn())
}
