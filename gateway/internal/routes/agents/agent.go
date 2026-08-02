package agents

import (
	"encoding/json"
	"fmt"
	"gateway/internal/svc/app"
	"gateway/pb"
	"github.com/zeromicro/go-zero/core/logx"
	"github.com/zeromicro/go-zero/rest/httpx"
	"google.golang.org/grpc/metadata"
	"io"
	"log"
	"net/http"
)

type ChatReq struct {
	Question string `json:"question"`
	ThreadId string `json:"threadId,omitempty"`
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

		logx.Debug()

		md := metadata.Pairs(
			"uid", ctx.Value("uid").(json.Number).String(),
			"Authorization", r.Header.Get("Authorization"),
		)
		//// 或者使用 map 方式: metadata.New(map[string]string{"authorization": authHeader, ...})
		//// 4. 将 metadata 注入到 context 中
		ctx = metadata.NewOutgoingContext(ctx, md)
		stream, err := agentRpc.Client().Chat(ctx, &pb.ChatRequest{
			Question: chatReq.Question,
			ThreadId: chatReq.ThreadId,
		})

		if err != nil {
			log.Fatal(err)
		}
		var resp *pb.ChatResponse

		for {
			var err error
			resp, err = stream.Recv()

			if err != nil {

				if err == io.EOF {
					// 流正常结束，发送结束事件
					fmt.Fprintf(w, resp.Data)
					if flusher, ok := w.(http.Flusher); ok {
						flusher.Flush()
					}
					break
				}

				logx.Errorf("receive error: %v", err)
				// 发送错误事件
				fmt.Fprintf(w, "event: error\ndata: %s\n\n", err.Error())
				if flusher, ok := w.(http.Flusher); ok {
					flusher.Flush()
				}
				return
			}

			// 构造JSON数据包含内容和is_end

			//
			//// 发送SSE事件
			fmt.Fprintf(w, resp.Data)
			if flusher, ok := w.(http.Flusher); ok {
				logx.Debug("resp.Data: ", resp.Data)
				flusher.Flush()
			}

		}

	}
}
