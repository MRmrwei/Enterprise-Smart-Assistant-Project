package middlewares

import (
	"bytes"
	"encoding/json"
	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/rest"
	"github.com/zeromicro/go-zero/rest/handler"
	"io"
	"net/http"
	"strings"
)

var whitelistPaths = []string{
	"/login", "/view",
}

func AuthWithWhitelist(secret string, opts ...handler.AuthorizeOption) rest.Middleware {
	// 获取原始认证中间件
	authMiddleware := handler.Authorize(secret, opts...)

	return func(next http.HandlerFunc) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {

			if shouldSkipMCPAuth(r) {
				// 跳过认证，直接执行
				next(w, r)
				return
			}

			// 检查是否在白名单中
			if isWhitelisted(r.URL.Path, whitelistPaths) {
				// 白名单路径跳过认证，直接执行
				next(w, r)
				return
			}

			// 需要认证的路径，使用原始认证中间件
			// 将 authMiddleware 转换为 Handler 并调用
			h := authMiddleware(http.HandlerFunc(func(w2 http.ResponseWriter, r2 *http.Request) {
				if uid, ok := r2.Context().Value("uid").(json.Number); ok {
					r2.Header.Set("X-uid", uid.String())
				}
				next(w2, r2)
			}))

			h.ServeHTTP(w, r)

		}
	}
}

func isWhitelisted(path string, whitelist []string) bool {
	for _, p := range whitelist {
		if strings.HasPrefix(path, p) || path == p {
			return true
		}
	}
	return false
}

// ShouldSkipMCPAuth 判断 MCP 请求是否应跳过认证
// 返回 true 表示跳过（非 tools/call 的 MCP 请求）
// 注意：此函数会读取并重置 r.Body，调用后 r.Body 可再次读取
func shouldSkipMCPAuth(r *http.Request) bool {
	// 1. 读取 Body
	bodyBytes, err := io.ReadAll(r.Body)
	if err != nil {
		logx.Errorf("ShouldSkipMCPAuth: failed to read body: %v", err)
		return false // 读取失败，不跳过（走认证）
	}
	// 2. 重置 Body，供后续使用
	r.Body = io.NopCloser(bytes.NewBuffer(bodyBytes))

	// 3. 解析 JSON，获取 method
	var mcpReq struct {
		Method string `json:"method"`
	}
	if err := json.Unmarshal(bodyBytes, &mcpReq); err != nil {
		// 不是合法 JSON 或没有 method 字段，视为非 MCP 请求
		return false
	}
	if mcpReq.Method == "" {
		return false // 不是 MCP 请求
	}

	// 4. 如果是 MCP 请求，且方法不是 "tools/call"，则跳过认证
	return mcpReq.Method != "tools/call"
}
