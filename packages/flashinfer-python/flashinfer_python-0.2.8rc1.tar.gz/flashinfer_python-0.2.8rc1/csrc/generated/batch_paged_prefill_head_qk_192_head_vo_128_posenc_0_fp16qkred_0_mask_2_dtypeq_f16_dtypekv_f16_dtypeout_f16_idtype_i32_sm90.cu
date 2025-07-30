 // batch_paged_prefill_sm90 template inst
#include <flashinfer/attention/hopper/default_params.cuh>
#include <flashinfer/attention/hopper/prefill_sm90.cuh>
#include <flashinfer/attention/hopper/variants.cuh>
#include <flashinfer/cutlass_utils.cuh>


namespace flashinfer {

using DTypeQ = cutlass_dtype_t<half>;
using DTypeKV = cutlass_dtype_t<half>;
using DTypeO = cutlass_dtype_t<half>;

using Params = BatchPrefillPagedParams<DTypeQ, DTypeKV, DTypeO, int32_t>;


template cudaError_t BatchPrefillWithPagedKVCacheDispatched
    <192,
     128,
     MaskMode::kCustom,
     /*USE_SLIDING_WINDOW=*/true,
     /*SAME_SCHEDULE_FOR_ALL_HEADS=*/true,
     LogitsSoftCap,
     Params>
    (Params& params, cudaStream_t stream);

template cudaError_t BatchPrefillWithPagedKVCacheDispatched
    <192,
     128,
     MaskMode::kCustom,
     /*USE_SLIDING_WINDOW=*/true,
     /*SAME_SCHEDULE_FOR_ALL_HEADS=*/false,
     LogitsSoftCap,
     Params>
    (Params& params, cudaStream_t stream);

template cudaError_t BatchPrefillWithPagedKVCacheDispatched
    <192,
     128,
     MaskMode::kCustom,
     /*USE_SLIDING_WINDOW=*/false,
     /*SAME_SCHEDULE_FOR_ALL_HEADS=*/true,
     LogitsSoftCap,
     Params>
    (Params& params, cudaStream_t stream);

template cudaError_t BatchPrefillWithPagedKVCacheDispatched
    <192,
     128,
     MaskMode::kCustom,
     /*USE_SLIDING_WINDOW=*/false,
     /*SAME_SCHEDULE_FOR_ALL_HEADS=*/false,
     LogitsSoftCap,
     Params>
    (Params& params, cudaStream_t stream);
    


template cudaError_t BatchPrefillWithPagedKVCacheDispatched
    <192,
     128,
     MaskMode::kCustom,
     /*USE_SLIDING_WINDOW=*/true,
     /*SAME_SCHEDULE_FOR_ALL_HEADS=*/true,
     StandardAttention,
     Params>
    (Params& params, cudaStream_t stream);

template cudaError_t BatchPrefillWithPagedKVCacheDispatched
    <192,
     128,
     MaskMode::kCustom,
     /*USE_SLIDING_WINDOW=*/true,
     /*SAME_SCHEDULE_FOR_ALL_HEADS=*/false,
     StandardAttention,
     Params>
    (Params& params, cudaStream_t stream);

template cudaError_t BatchPrefillWithPagedKVCacheDispatched
    <192,
     128,
     MaskMode::kCustom,
     /*USE_SLIDING_WINDOW=*/false,
     /*SAME_SCHEDULE_FOR_ALL_HEADS=*/true,
     StandardAttention,
     Params>
    (Params& params, cudaStream_t stream);

template cudaError_t BatchPrefillWithPagedKVCacheDispatched
    <192,
     128,
     MaskMode::kCustom,
     /*USE_SLIDING_WINDOW=*/false,
     /*SAME_SCHEDULE_FOR_ALL_HEADS=*/false,
     StandardAttention,
     Params>
    (Params& params, cudaStream_t stream);
    

}