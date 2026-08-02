package mcp

import (
	"ai/service-mcp/internal/config"
	"github.com/mark3labs/mcp-go/server"
	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/rest"
	"net/http"
)

type mcpserver struct {
	McpServer  *server.MCPServer
	server     *rest.Server
	httpServer *server.StreamableHTTPServer
	c          config.McpConfig
}

func NewMCPServer(config config.McpConfig) *mcpserver {
	//auth := server.WithToolHandlerMiddleware(middlewares.AuthMiddleware)
	return &mcpserver{
		McpServer: server.NewMCPServer(config.McpName, config.Version),
		c:         config,
	}
}
func (this *mcpserver) Start() {

	this.server = rest.MustNewServer(this.c.RestConf)

	httpServer := server.NewStreamableHTTPServer(this.McpServer)

	this.server.AddRoutes([]rest.Route{
		{
			Method:  http.MethodPost,
			Path:    "/mcp",
			Handler: httpServer.ServeHTTP,
		},
	})

	logx.Debugf("mcp服务器启动")
	this.server.Start()
}

func (this *mcpserver) Stop() {
	this.server.Stop()
}
