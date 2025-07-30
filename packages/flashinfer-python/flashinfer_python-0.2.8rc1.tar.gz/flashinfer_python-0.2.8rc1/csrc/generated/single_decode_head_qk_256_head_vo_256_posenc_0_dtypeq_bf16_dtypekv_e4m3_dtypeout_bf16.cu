#include <flashinfer/attention_impl.cuh>

namespace flashinfer {

using Params = SingleDecodeParams<nv_bfloat16, __nv_fp8_e4m3, nv_bfloat16>;

template cudaError_t SingleDecodeWithKVCacheDispatched<256, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    nv_bfloat16* tmp,
    cudaStream_t stream);

template cudaError_t SingleDecodeWithKVCacheDispatched<256, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    nv_bfloat16* tmp,
    cudaStream_t stream);

template cudaError_t SingleDecodeWithKVCacheDispatched<256, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    nv_bfloat16* tmp,
    cudaStream_t stream);

template cudaError_t SingleDecodeWithKVCacheDispatched<256, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    nv_bfloat16* tmp,
    cudaStream_t stream);

}
    