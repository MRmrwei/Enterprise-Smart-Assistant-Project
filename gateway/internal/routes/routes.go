package routes

import (
	"gateway/internal/routes/agents"
	"gateway/internal/svc/app"
	"github.com/zeromicro/go-zero/gateway"
	"github.com/zeromicro/go-zero/rest"
	"net/http"
)

func Register(server *gateway.Server, app app.Application) {

	for _, agentAddr := range app.Config().AgentAddr {
		server.AddRoute(rest.Route{
			Method:  http.MethodPost,
			Path:    agentAddr.Path,
			Handler: agents.Chat(agentAddr).ServeHTTP,
		}, rest.WithSSE(), rest.WithTimeout(0))
	}

}
