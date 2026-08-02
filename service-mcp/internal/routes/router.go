package routes

import (
	"ai/service-mcp/internal/svc/app"
	"ai/service-mcp/internal/tools"
	"github.com/mark3labs/mcp-go/server"
)

func ToolRegister(s *server.MCPServer, app app.Application) {
	s.AddTools(tools.EmployeeInfoTool(app))
}
