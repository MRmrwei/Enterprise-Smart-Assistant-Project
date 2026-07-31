package routes

import (
	"gateway/internal/routes/agents"
	"gateway/internal/svc/app"
	"github.com/zeromicro/go-zero/gateway"
	"github.com/zeromicro/go-zero/rest"
	"net/http"
)

func Register(server *gateway.Server, app app.Application) {
	server.AddRoute(rest.Route{
		Method:  http.MethodPost,
		Path:    "/agent/chat",
		Handler: agents.Chat(app),
	}, rest.WithSSE(), rest.WithTimeout(0))

	server.AddRoute(rest.Route{
		Method:  http.MethodGet,
		Path:    "/view/:file",
		Handler: http.StripPrefix("/view/", http.FileServer(http.Dir("./view"))).ServeHTTP,
	})

}
