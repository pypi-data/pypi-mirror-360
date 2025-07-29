import equinox as eqx
import jax
import jax.numpy as jnp

import evermore as evm


class LinearConstrained(eqx.Module):
    weights: evm.Parameter
    biases: jax.Array

    def __init__(self, in_size, out_size, key):
        wkey, bkey = jax.random.split(key)
        # weights
        normal = evm.pdf.Normal(
            mean=jnp.zeros((out_size, in_size)),
            width=jnp.full((out_size, in_size), 0.5),
        )
        self.weights = evm.Parameter(
            value=jax.random.normal(wkey, (out_size, in_size)),
            lower=-jnp.inf,  # type: ignore[arg-type]
            upper=jnp.inf,  # type: ignore[arg-type]
            prior=normal,
        )

        # biases
        self.biases = jax.random.normal(bkey, (out_size,))

    def __call__(self, x: jax.Array):
        return self.weights.value @ x + self.biases


@eqx.filter_jit
def loss_fn(model, x, y):
    pred_y = jax.vmap(model)(x)
    mse = jax.numpy.mean((y - pred_y) ** 2)
    constraints = evm.loss.get_log_probs(model)
    # sum them all up for each weight
    constraints = jax.tree.map(jnp.sum, constraints)
    return mse + evm.util.sum_over_leaves(constraints)


if __name__ == "__main__":
    batch_size, in_size, out_size = 32, 2, 3
    model = LinearConstrained(in_size, out_size, key=jax.random.PRNGKey(0))
    x = jax.numpy.zeros((batch_size, in_size))
    y = jax.numpy.zeros((batch_size, out_size))
    loss_val = loss_fn(model, x, y)
    grads = eqx.filter_grad(loss_fn)(model, x, y)
