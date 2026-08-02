package tools

import (
	"ai/service-mcp/internal/svc/app"
	"context"
	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
	"github.com/zeromicro/go-zero/core/logx"
)

func EmployeeInfoTool(app app.Application) server.ServerTool {
	tool := mcp.NewTool("employee_info",
		mcp.WithDescription("获取员工信息"),
		mcp.WithString("name", mcp.Required(), mcp.Description("员工姓名")),
	)
	return server.ServerTool{
		Tool: tool,
		Handler: func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
			logx.Debug("EmployeeInfoTool ", request.Header)
			return nil, nil
		},
	}
}
