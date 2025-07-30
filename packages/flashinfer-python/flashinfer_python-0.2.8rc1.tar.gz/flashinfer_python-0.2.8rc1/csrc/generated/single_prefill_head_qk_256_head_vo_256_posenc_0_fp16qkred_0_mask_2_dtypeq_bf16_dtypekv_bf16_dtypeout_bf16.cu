#include <flashinfer/attention_impl.cuh>

namespace flashinfer {

using Params = SinglePrefillParams<nv_bfloat16, nv_bfloat16, nv_bfloat16>;

template cudaError_t SinglePrefillWithKVCacheDispatched<256, 256, PosEncodingMode::kNone, 0, MaskMode::kCustom, DefaultAttention<
    true, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    nv_bfloat16* tmp,
    cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched<256, 256, PosEncodingMode::kNone, 0, MaskMode::kCustom, DefaultAttention<
    true, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    nv_bfloat16* tmp,
    cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched<256, 256, PosEncodingMode::kNone, 0, MaskMode::kCustom, DefaultAttention<
    true, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    nv_bfloat16* tmp,
    cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched<256, 256, PosEncodingMode::kNone, 0, MaskMode::kCustom, DefaultAttention<
    true, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    nv_bfloat16* tmp,
    cudaStream_t stream);

}
    