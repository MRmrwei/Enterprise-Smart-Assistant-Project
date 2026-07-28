package agents

import (
	"encoding/json"
	"fmt"
	"gateway/internal/svc/app"
	"gateway/pb"
	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/rest/httpx"
	"io"
	"log"
	"net/http"
)

type ChatReq struct {
	Question string `json:"question"`
}

func (Chat *ChatReq) Validate() error {
	logx.Debug("Validate func")
	return nil
}
func Chat(agentRpc app.AgentRpc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var chatReq ChatReq

		if err := httpx.Parse(r, &chatReq); err != nil {
			logx.Debug("err = ", err)
			return
		}

		ctx := r.Context()
		stream, err := agentRpc.Client().Chat(ctx, &pb.ChatRequest{
			Question: chatReq.Question,
		})

		if err != nil {
			log.Fatal(err)
		}
		var resp *pb.ChatResponse

		for {
			var err error
			resp, err = stream.Recv()
			if err == io.EOF {
				// 流正常结束，发送结束事件
				fmt.Fprintf(w, "event: end\ndata: {}\n\n")
				if flusher, ok := w.(http.Flusher); ok {
					flusher.Flush()
				}
				break
			}
			if err != nil {
				logx.Errorf("receive error: %v", err)
				// 发送错误事件
				fmt.Fprintf(w, "event: error\ndata: %s\n\n", err.Error())
				if flusher, ok := w.(http.Flusher); ok {
					flusher.Flush()
				}
				return
			}

			// 构造JSON数据包含内容和is_end
			data := map[string]interface{}{
				"content": resp.Message,
				"is_end":  resp.IsEnd,
			}
			jsonData, _ := json.Marshal(data)

			// 发送SSE事件
			fmt.Fprintf(w, "event: %s\ndata: %s\n\n", resp.Event, string(jsonData))
			if flusher, ok := w.(http.Flusher); ok {
				flusher.Flush()
			}

			// 如果收到end事件，退出循环（但已发送该事件）
			if resp.Event == "end" {
				break
			}
		}

	}
}
