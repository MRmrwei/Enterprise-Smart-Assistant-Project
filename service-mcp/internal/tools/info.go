package tools

import (
	"ai/service-mcp/internal/services"
	"ai/service-mcp/internal/svc/app"
	"ai/service-mcp/internal/tools/types"
	"context"
	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
	"github.com/zeromicro/go-zero/core/logc"
	"github.com/zeromicro/go-zero/core/logx"
	"strconv"
)

func EmployeeInfoTool(app app.Application) server.ServerTool {
	tool := mcp.NewTool("employee_info",
		mcp.WithDescription("获取员工个人信息请调用此工具"),
		mcp.WithString("name", mcp.Required(), mcp.Description("员工姓名")),
		mcp.WithOutputSchema[types.EmployeeInfoResponse](),
	)
	return server.ServerTool{
		Tool: tool,
		Handler: func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {

			uid, err := strconv.ParseInt(request.Header.Get("X-uid"), 10, 64)
			if err != nil {
				logc.Error(ctx, "parse int error:", err)
				return nil, err
			}

			service := services.NewEmployeeService(app.DB())
			res, err := service.Info(ctx, uid)
			if err != nil {
				logx.Debug("err =", err.Error())
			}

			return mcp.NewToolResultStructured(res, ""), err
		},
	}
}
