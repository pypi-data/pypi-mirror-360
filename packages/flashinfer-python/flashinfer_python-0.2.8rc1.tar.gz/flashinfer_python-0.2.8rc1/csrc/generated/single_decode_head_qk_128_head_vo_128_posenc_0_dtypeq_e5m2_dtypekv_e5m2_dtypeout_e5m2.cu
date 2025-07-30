#include <flashinfer/attention_impl.cuh>

namespace flashinfer {

using Params = SingleDecodeParams<__nv_fp8_e5m2, __nv_fp8_e5m2, __nv_fp8_e5m2>;

template cudaError_t SingleDecodeWithKVCacheDispatched<128, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    __nv_fp8_e5m2* tmp,
    cudaStream_t stream);

template cudaError_t SingleDecodeWithKVCacheDispatched<128, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/false, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    __nv_fp8_e5m2* tmp,
    cudaStream_t stream);

template cudaError_t SingleDecodeWithKVCacheDispatched<128, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/false, /*use_alibi_bias=*/false>, Params>(
    Params params,
    __nv_fp8_e5m2* tmp,
    cudaStream_t stream);

template cudaError_t SingleDecodeWithKVCacheDispatched<128, PosEncodingMode::kNone, DefaultAttention<
    /*use_custom_mask=*/false, /*use_sliding_window=*/true, /*use_logits_soft_cap=*/true, /*use_alibi_bias=*/false>, Params>(
    Params params,
    __nv_fp8_e5m2* tmp,
    cudaStream_t stream);

}
    