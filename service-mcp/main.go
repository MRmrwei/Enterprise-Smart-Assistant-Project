package main

import (
	"ai/service-mcp/internal/config"
	"ai/service-mcp/internal/mcp"
	"ai/service-mcp/internal/routes"
	"ai/service-mcp/internal/server"
	"ai/service-mcp/internal/svc"
	"ai/service-mcp/pb"
	"flag"
	"fmt"
	"github.com/zeromicro/go-zero/core/conf"
	"github.com/zeromicro/go-zero/core/service"
	"github.com/zeromicro/go-zero/zrpc"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

var configFile = flag.String("f", "etc/main.yaml", "the config file")

func main() {
	flag.Parse()

	var c config.Config

	conf.MustLoad(*configFile, &c)
	ctx := svc.NewServiceContext(c)
	master := service.NewServiceGroup()
	s := zrpc.MustNewServer(c.RpcServerConf, func(grpcServer *grpc.Server) {
		pb.RegisterRpcServer(grpcServer, server.NewRpcServer(ctx))

		if c.Mode == service.DevMode || c.Mode == service.TestMode {
			reflection.Register(grpcServer)
		}
	})

	mcpserver := mcp.NewMCPServer(c.McpConfig)
	routes.ToolRegister(mcpserver.McpServer, ctx)
	master.Add(mcpserver)
	master.Add(s)
	defer master.Stop()

	fmt.Printf("Starting rpc server at %s...\n", c.ListenOn)

	master.Start()
}
