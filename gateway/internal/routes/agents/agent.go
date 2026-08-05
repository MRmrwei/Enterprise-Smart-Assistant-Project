package agents

import (
	"gateway/internal/config"
	"github.com/zeromicro/go-zero/core/logx"
	"net/http"
	"net/http/httputil"
	"net/url"
)

type ChatReq struct {
	Question string `json:"question"`
	ThreadId string `json:"threadId,omitempty"`
}

func (Chat *ChatReq) Validate() error {
	logx.Debug("Validate func")
	return nil
}
func Chat(agentAddr config.AgentAddr) *httputil.ReverseProxy {
	target, _ := url.Parse(agentAddr.Host) // 你的后端服务地址

	// 2. 创建反向代理，并自定义 Director
	proxy := httputil.NewSingleHostReverseProxy(target)
	originalDirector := proxy.Director
	proxy.Director = func(req *http.Request) {
		originalDirector(req)
		// 关键：修改请求的路径，指向后端实际的 SSE 端点
		req.URL.Path = agentAddr.Path // 你的后端 SSE 实际路径
		// 如果需要，可以在这里修改 Header，例如 Host
		// req.Host = "your-backend-host"
	}

	return proxy
}
