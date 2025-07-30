#include <flashinfer/attention_impl.cuh>

namespace flashinfer {

using Params = SinglePrefillParams<half, __nv_fp8_e5m2, half>;

template cudaError_t SinglePrefillWithKVCacheDispatched<128, 128, PosEncodingMode::kNone, 0, MaskMode::kCustom, DefaultAttention<
    true, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    half* tmp,
    cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched<128, 128, PosEncodingMode::kNone, 0, MaskMode::kCustom, DefaultAttention<
    true, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    half* tmp,
    cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched<128, 128, PosEncodingMode::kNone, 0, MaskMode::kCustom, DefaultAttention<
    true, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    half* tmp,
    cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched<128, 128, PosEncodingMode::kNone, 0, MaskMode::kCustom, DefaultAttention<
    true, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    half* tmp,
    cudaStream_t stream);

}
    