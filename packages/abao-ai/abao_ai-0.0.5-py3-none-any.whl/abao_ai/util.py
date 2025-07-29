from cuda.bindings.runtime import cudaError_t


def _ccr(cuda_ret):
    cuda_error: cudaError_t = cuda_ret[0]
    if cuda_error != cudaError_t.cudaSuccess:
        raise RuntimeError(f"{cuda_error}")
    assert len(cuda_ret) == 2
    return cuda_ret[1]


def _cce(cuda_ret):
    cuda_error: cudaError_t = cuda_ret[0]
    if cuda_error != cudaError_t.cudaSuccess:
        raise RuntimeError(f"{cuda_error}")
