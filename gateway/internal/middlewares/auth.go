package middlewares

import (
	"encoding/json"
	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/rest"
	"github.com/zeromicro/go-zero/rest/handler"
	"net/http"
	"strings"
)

var whitelistPaths = []string{
	"/login",
}

func AuthWithWhitelist(secret string, opts ...handler.AuthorizeOption) rest.Middleware {
	// 获取原始认证中间件
	authMiddleware := handler.Authorize(secret, opts...)

	return func(next http.HandlerFunc) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
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
	logx.Debug("path = ", path)
	for _, p := range whitelist {
		if strings.HasPrefix(path, p) || path == p {
			return true
		}
	}
	return false
}
