 // single_prefill_sm90 template inst
#include <flashinfer/attention/hopper/default_params.cuh>
#include <flashinfer/attention/hopper/prefill_sm90.cuh>
#include <flashinfer/attention/hopper/variants.cuh>
#include <flashinfer/cutlass_utils.cuh>

namespace flashinfer {

using DTypeQ = cutlass_dtype_t<half>;
using DTypeKV = cutlass_dtype_t<half>;
using DTypeO = cutlass_dtype_t<half>;

using Params = SinglePrefillParams<DTypeQ, DTypeKV, DTypeO>;

template cudaError_t SinglePrefillWithKVCacheDispatched
    <256, 256, MaskMode::kNone, /*USE_SLIDING_WINDOW=*/true, LogitsSoftCap, Params>
    (Params& params, cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched
    <256, 256, MaskMode::kNone, /*USE_SLIDING_WINDOW=*/false, LogitsSoftCap, Params>
    (Params& params, cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched
    <256, 256, MaskMode::kNone, /*USE_SLIDING_WINDOW=*/true, StandardAttention, Params>
    (Params& params, cudaStream_t stream);

template cudaError_t SinglePrefillWithKVCacheDispatched
    <256, 256, MaskMode::kNone, /*USE_SLIDING_WINDOW=*/false, StandardAttention, Params>
    (Params& params, cudaStream_t stream);

}
    