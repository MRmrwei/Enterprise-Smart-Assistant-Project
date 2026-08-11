import asyncio
import os
import tempfile
from dataclasses import dataclass
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException

from pydantics.response import ApiResponse
from services.rags.rag import RagUploadService

router = APIRouter()

MAX_FILES = 10


@dataclass
class UploadRagFileRequest:
    """上传 RAG 文件请求参数"""

    doc_type: str = Form(..., description="文档类型")
    department: str = Form(..., description="所属部门")
    version: str = Form(..., description="版本号")
    chunk_strategy: str = Form("", description="切块策略：parent_child / general")


@router.post("/upload_rag_file", response_model=ApiResponse[dict])
async def upload_rag_file(
    req: UploadRagFileRequest = Depends(),
    files: List[UploadFile] = File(..., description="上传文件列表，最多10个"),
):
    """接收多个文件（最多10个），写入临时文件，处理完后自动删除"""

    # --- 校验 ---
    if not files:
        raise HTTPException(status_code=400, detail="至少上传一个文件")

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"单次最多上传 {MAX_FILES} 个文件，当前选择了 {len(files)} 个",
        )

    for f in files:
        if f.filename and not f.filename.lower().endswith(".txt"):
            raise HTTPException(
                status_code=400,
                detail=f"文件「{f.filename}」不是 TXT 格式，仅支持 .txt 文本文件",
            )

    # --- 逐个写入临时文件 ---
    saved_files = []
    total_size = 0
    failed_files = []

    for idx, file in enumerate(files):
        try:
            content = await file.read()
            file_size = len(content)
            total_size += file_size

            original_ext = os.path.splitext(file.filename or "upload.txt")[1] or ".txt"
            tmp = tempfile.NamedTemporaryFile(
                delete=False,
                prefix=f"rag_{req.doc_type}_{idx}_",
                suffix=original_ext,
            )
            tmp.write(content)
            tmp.close()

            saved_files.append(
                {
                    "index": idx,
                    "filename": file.filename,
                    "tmp_path": tmp.name,
                    "size": file_size,
                }
            )

        except Exception as e:
            failed_files.append(
                {
                    "index": idx,
                    "filename": file.filename or f"file_{idx}",
                    "error": str(e),
                }
            )

    # --- 文件处理 & 自动清理 ---
    process_results = []
    ragUploadService = RagUploadService()
    try:
        # ===文件处理逻辑===
        for item in saved_files:
            try:
                print(f"处理文件：{item}")
                await ragUploadService.upload(
                    item["tmp_path"],
                    item["filename"],
                    req.chunk_strategy,
                    req.department,
                    req.version,
                    req.doc_type,
                )
                print("处理完成")
                # await asyncio.sleep(1)
                process_results.append({"filename": item["filename"], "success": True})
            except Exception as e:
                process_results.append(
                    {"filename": item["filename"], "success": False, "error": str(e)}
                )
        # ========================================
    finally:
        for item in saved_files:
            try:
                os.unlink(item["tmp_path"])
            except OSError:
                pass

    success_count = sum(1 for r in process_results if r["success"])
    fail_count = sum(1 for r in process_results if not r["success"])

    return ApiResponse(
        success=True,
        message=f"处理完成：成功 {success_count}，失败 {fail_count}（请重新上传失败文件）",
        data={
            "total": len(files),
            "success_count": success_count,
            "fail_count": fail_count,
            "results": process_results,
        },
    )
