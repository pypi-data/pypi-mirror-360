#include <flashinfer/attention_impl.cuh>

namespace flashinfer {

using Params = BatchDecodeParams<half, __nv_fp8_e4m3, half, int32_t>;

template cudaError_t BatchDecodeWithPagedKVCacheDispatched<128, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    half* tmp_v, float* tmp_s,
    cudaStream_t stream);

template cudaError_t BatchDecodeWithPagedKVCacheDispatched<128, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    half* tmp_v, float* tmp_s,
    cudaStream_t stream);

template cudaError_t BatchDecodeWithPagedKVCacheDispatched<128, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    half* tmp_v, float* tmp_s,
    cudaStream_t stream);

template cudaError_t BatchDecodeWithPagedKVCacheDispatched<128, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    half* tmp_v, float* tmp_s,
    cudaStream_t stream);

using ParamsMlaT = BatchDecodeParamsMLA<half, __nv_fp8_e4m3, half, int32_t>;

template cudaError_t BatchDecodeWithPagedKVCacheDispatchedMLA<128, 16, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, ParamsMlaT>(
    ParamsMlaT params,
    half* tmp_v, float* tmp_s,
    cudaStream_t stream);

}
    