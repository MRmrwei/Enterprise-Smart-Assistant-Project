package agents

import (
	"io"
	"net/http"

	"gateway/internal/config"
	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/rest/httpc"
)

// Chat 返回一个 HTTP Handler，用于将请求转发到后端 SSE 服务
func Chat(agentAddr config.AgentAddr) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		// 1. 构造后端完整 URL
		targetURL := agentAddr.Host + agentAddr.Path

		// 2. 创建转发请求（复用原始请求的 Context、Method、Body 和 Header）
		req, err := http.NewRequestWithContext(r.Context(), r.Method, targetURL, r.Body)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		req.Header = r.Header.Clone() // 克隆原始 Header（含认证等）

		// 3. 使用 httpc 发起请求（自动注入 traceparent 等头）
		resp, err := httpc.DoRequest(req)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadGateway)
			return
		}
		defer resp.Body.Close()

		// 4. 复制后端响应的 Header 到客户端响应
		for key, values := range resp.Header {
			for _, value := range values {
				w.Header().Add(key, value)
			}
		}
		w.WriteHeader(resp.StatusCode)

		// 5. 获取 Flusher（用于强制刷新）
		flusher, ok := w.(http.Flusher)
		if !ok {
			http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
			return
		}

		// 6. 流式复制响应体，每次写入后立即 Flush
		buf := make([]byte, 32*1024) // 32KB 缓冲区
		for {
			n, err := resp.Body.Read(buf)
			if n > 0 {
				if _, writeErr := w.Write(buf[:n]); writeErr != nil {
					return // 客户端已断开，停止复制
				}
				flusher.Flush() // 强制将数据发送给客户端
			}
			if err != nil {
				if err != io.EOF {
					logx.Errorf("Stream copy error: %v", err)
				}
				return
			}
		}
	}
}
