"""A generic dataloader."""

# Author: Peishi Jiang <shixijps@gmail.com>
#
# The dataloader codes is revised from an early PyTorch implementation
# written by Nis Meinert in the NASA FDL 2021 bootcamp.
#
# I adapted the codes to be compatible with JAX.


from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import jax
import jax.numpy as jnp
from jaxlib.xla_extension import Device
from jaxtyping import Array


class BatchedDL:
    """Batched data loader.

    Wraps an iterable and yields its values in batches.

    :param it: An iterable over pairs of tensors.
    :param batch_size: The batch size.
    :param device: The ``jax.devices`` on which tensors should be stored.
    """

    def __init__(
        self,
        it: Iterable[Tuple[Array, Array]],
        batch_size: int,
        device: Optional[Device] = None,
    ) -> None:
        self.it = it
        self.data = iter(self.it)
        self.batch_size = batch_size
        self.device = device

    def __iter__(self):
        self.data = iter(self.it)
        return self

    def __next__(self):
        first = next(self.data)
        x, y = [], []
        x.append(first[0])
        y.append(first[1])

        last = 1
        for i in range(1, self.batch_size):
            try:
                then = next(self.data)
                x.append(then[0])
                y.append(then[1])
                last = i + 1
            except StopIteration:
                last = i
                break
        x = jax.device_put(jnp.stack(x), device=self.device)
        y = jax.device_put(jnp.stack(y), device=self.device)

        return x[:last], y[:last]


class MultiDL:
    """Gathering of data loader.

    Gathers data loaders, initializes and iterates them in sequence.

    :param DL: Data loader class.
    :param args: Unnamed arguments for each data loader constructor.
    :param kwargs: Named arguments for each data loader constructor.
    """

    def __init__(self, DL, args: List[Any], kwargs: List[Dict[str, Any]]) -> None:
        if len(args) != len(kwargs):
            raise ValueError("Number of unnamed and named arguments has to match.")

        self.DL = DL
        self.args = args
        self.kwargs = kwargs

        self.dl = None
        self.n = len(args)
        self.i = self.n

    def _load_next_dl(self):
        idx = -self.i
        self.i -= 1

        if self.i < 0:
            raise StopIteration

        args = self.args[idx]
        kwargs = self.kwargs[idx]

        return self.DL(*args, **kwargs)

    def __iter__(self):
        self.i = self.n
        return self

    def __next__(self):
        if self.dl is None:
            self.dl = self._load_next_dl()

        try:
            return next(self.dl)
        except StopIteration:
            self.dl = self._load_next_dl()
            return next(self.dl)


class DataSet:
    """Lazily concatenates features of consecutive elements.

    Given sequences of ``f`` features with ``n`` elements for ``x`` and ``m < n`` elements for ``y``
    this iterator will stack ``n - m + 1`` consecutive elements in the last dimension for ``x`` and
    yield those together with the corresponding value in ``y``. This stacking happens lazily on each
    yield of the iterator.

    For example, given ``(8, 11, 13, 7)`` and ``(5, 11, 13, 1)`` for ``x`` and ``y``, respectively,
    i.e., ``n=8``, ``m=5`` and ``f=7``, the iterator will yield 5 tuples of size:

      1. ``((11, 13, 28), (11, 13, 1))``,
      2. ``((11, 13, 28), (11, 13, 1))``,
      3. ``((11, 13, 28), (11, 13, 1))``,
      4. ``((11, 13, 28), (11, 13, 1))``,
      5. ``((11, 13, 28), (11, 13, 1))``.

    The enlarged feature dimension of the first element of each tuple is the product of
    ``(n - m + 1) x f`` where the first tuple is the result of stacking the elements of the
    first 4 features in ``x`` on top of each other. Similarly, the second tuple is the result
    of the 2nd, 3rd, 4th and 5th element, etc.

    :param x: Input tensor of shape ``(n, *, f)``.
    :param y: Input tensor of shape ``(n, *)``.
    :param statics: Indices of features that should not be stacked.
    :param n_repeat: Number of sequence repetitions.
    :param seed: If not ``None``, this value is used to seed a random engine and the tuples are
                 shuffled upon return.
    :param device: The ``torch.device`` on which tensors should be stored.
    """

    def __init__(
        self,
        x: Any,
        y: Any,
        statics: Optional[List[int]] = None,
        n_repeat: int = 0,
        seed: Optional[int] = None,
        device: Optional[Device] = None,
    ) -> None:
        self.device = device

        if statics is None:
            statics = []

        if not all([0 <= i < x.shape[-1] for i in statics]):
            raise ValueError("Found invalid index in statics.")

        x = jax.device_put(x, device)
        y = jax.device_put(y, device)

        sel = [i not in statics for i in range(x.shape[-1])]
        sel = jax.device_put(jnp.array(sel), device=device)

        self.x = x[..., sel]
        self.y = y
        self.statics = x[..., ~sel]

        self.i = 0
        self.j = n_repeat
        self.n = self.y.shape[0]
        self.n_stack = self.x.shape[0] - self.n
        self.n_repeat = n_repeat

        # self.rng = np.random.default_rng(seed) if seed else None
        self.key = jax.random.key(seed) if seed else None
        self.idx = self._generate_idx()

    def _generate_idx(self):
        idx = jnp.arange(self.n) + self.n_stack
        if self.key is not None:
            # Perform the shuffle
            idx = jax.random.permutation(self.key, idx)
            # Update the key
            _, newkey = jax.random.split(self.key)
            self.key = newkey
        return jax.device_put(idx, device=self.device)

    def __iter__(self):
        self.i = 0
        self.j = self.n_repeat
        return self

    def __next__(self):
        if self.i >= self.n:
            self.i = 0
            self.j -= 1
            self.idx = self._generate_idx()

        if self.j < 0:
            raise StopIteration

        i = self.idx[self.i]
        self.i += 1

        return (
            jnp.concat(
                [self.x[j] for j in range(i - self.n_stack, i + 1)]
                + [self.statics[i - self.n_stack]],
                axis=-1,
            ),
            self.y[i - self.n_stack],
        )


def make_big_data_loader(
    x: Any,
    y: Any,
    statics: Any=None,
    chunk_size: int=None,
    n_hist: int=0,
    n_fut: int=0,
    n_repeat: Optional[int] = 0,
    batch_size: Optional[int] = None,
    dl_seed: Optional[int] = None,
    device: Optional[Device] = None,
) -> Union[BatchedDL, MultiDL]:
    """Returns wrapped :class:`LazyFeatureCat` instances.

    The input data is divided into chunks and :class:`DataSet` instances are created for each
    chunk.

    :param x: Divided into chunks and forwarded as ``x`` to :class:`DataSet`.
    :param y: Divided into chunks and forwarded as ``y`` to :class:`DataSet`.
    :param statics: Indices of static features (see :class:`DataSet` for more details).
    :param chunk_size: Chunk size.
    :param n_hist: Number of events to be stacked by :class:`DataSet` on top of each element.
    :param n_fut: Offset of ``y`` w.r.t. to current index.
    :param n_repeat: See :class:`DataSet` for details.
    :param batch_size: If not ``None`` the result of :class:`DataSet` are gathered in batches
                       of the given size.
    :param dl_seed: See :class:`DataSet` for details.
    :param device: The ``jax.device`` on which tensors should be stored.
    :return: An iterable that wraps :class:`DataSet` instances for each chunk.
    """
    nsample = x.shape[0]
    
    if chunk_size is None:
        chunk_size = nsample

    if chunk_size < n_hist:
        raise ValueError("The history size cannot be smaller than the chunk size.")

    min_length = n_hist + 1
    o1 = n_hist
    o2 = o1 + n_fut

    args = []
    for i in range(0, x.shape[0], chunk_size):
        x_first = i
        x_last = min(x_first + chunk_size, x.shape[0])
        n_x = x_last - x_first

        n_y = n_x - n_hist
        y_first = o2 + i
        y_last = min(y_first + n_y, y.shape[0])
        dn = n_y - (y_last - y_first)

        x_last -= dn
        n_x -= dn

        if n_x >= min_length:
            args.append((x[x_first:x_last], y[y_first:y_last], statics))

    kwargs = [{"n_repeat": n_repeat, "seed": dl_seed, "device": device}] * len(args)

    dl = MultiDL(DataSet, args, kwargs)
    return BatchedDL(dl, batch_size=batch_size, device=device) if batch_size else dl



# def make_huge_lazy_cat(
#     x: Any,
#     y: Any,
#     xind: List,
#     yind: List,
#     statics: List,
#     chunk_size: int,
#     n_hist: int,
#     n_fut: int,
# #     xind: Optional[list] = None,
# #     yind: Optional[list] = None,
#     n_repeat: Optional[int] = 0,
#     batch_size: Optional[int] = None,
#     seed: Optional[int] = None,
#     device: Optional[str] = None,
# ) -> Union[BatchedDL, BigDL]:
#     """Returns wrapped :class:`LazyFeatureCat` instances.

#     The input data is divided into chunks and :class:`LazyFeatureCat` instances are created for each
#     chunk.

#     :param x: See :class:`make_big_lazy_cat` for details.
#     :param y: See :class:`make_big_lazy_cat` for details.
#     :param xind: A list of feature indices to be substracted for x (assuming the last dimension is feature dimension).
#     :param yind: A list of feature indices to be substracted for y (assuming the last dimension is feature dimension).
#     :param statics: See :class:`make_big_lazy_cat` for details.
#     :param chunk_size: See :class:`make_big_lazy_cat` for details.
#     :param n_hist: See :class:`make_big_lazy_cat` for details.
#     :param n_fut: See :class:`make_big_lazy_cat` for details.x.
#     :param n_repeat: See :class:`LazyFeatureCat` for details.
#     :param batch_size: See :class:`make_big_lazy_cat` for details.
#     :param seed: See :class:`make_big_lazy_cat` for details.
#     :param device: See :class:`make_big_lazy_cat` for details.
#     :return: An iterable that wraps :class:`LazyFeatureCat` instances for each chunk.
#     """
#     xsub = x[..., xind+statics] if xind else x
#     ysub = y[..., yind] if yind else y
    
#     staticssub = [(xind+statics).index(s) for s in statics] if xind else statics
    
# #     print(xsub.shape, ysub.shape)
# #     print(xind+statics, staticssub, statics)
    
#     return make_big_lazy_cat(xsub, ysub, staticssub, chunk_size, n_hist, n_fut, 
#                              n_repeat, batch_size, seed, device)