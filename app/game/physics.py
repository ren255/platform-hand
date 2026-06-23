
def _resolve_vertical_collisions(rect, vel_y, blocks):
    """Resolve vertical collisions between `rect` and fixed `blocks`.

    Returns (rect, vel_y, on_ground).
    """

    on_ground = False
    for block in blocks:
        if rect.colliderect(block):
            if vel_y > 0 and rect.bottom - vel_y <= block.top + 1:
                rect.bottom = block.top
                vel_y = 0
                on_ground = True
            elif vel_y < 0 and rect.top - vel_y >= block.bottom - 1:
                rect.top = block.bottom
                vel_y = 0
    return rect, vel_y, on_ground


def _resolve_horizontal_collisions(rect, moving_left, moving_right, blocks):
    """Simple push-out against blocks for horizontal movement."""

    for block in blocks:
        if rect.colliderect(block):
            if moving_right and not moving_left:
                rect.right = block.left
            elif moving_left and not moving_right:
                rect.left = block.right
    return rect



def _check_spike_collision(rect, spikes):
    """Return True if rect touches any spike. No resolution — instant death."""
    return any(rect.colliderect(spike) for spike in spikes)