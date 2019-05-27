#
# This is simulation of cart-poles apparatus with two poles based on the Newton laws
# which use Runge-Kutta fourth-order method for numerical approximation of system dynamics.
#
import math
import random

#
# The constants defining physics of cart-2-poles apparatus
#
GRAVITY = -9.8  # m/s^2 - here negative as equations of motion for 2-pole system assume it to be negative
MASS_CART = 1.0 # kg
FORCE_MAG = 10.0 # N
# The first pole
MASS_POLE_1 = 1.0 # kg
LENGTH_1 = 0.5  # m - actually half the first pole's length
# The second pole
MASS_POLE_2 = 0.1 # kg
LENGTH_2 = 0.05 # m - actually half the second pole's length
# The coefficient of friction of pivot of the pole
MUP = 0.000002

# The maximum allowed angle of pole fall from the vertical
THIRTY_SIX_DEG_IN_RAD = (36 * math.pi) / 180.0 # rad

def calc_step(action, x, x_dot, theta1, theta1_dot, theta2, theta2_dot):
    """
    The function to perform calculations of system dynamics for one step
    of simulations.
    Arguments:
        action:     The binary action defining direction of
                    force to be applied.
        x:          The current cart X position
        x_dot:      The velocity of the cart
        theta1:      The current angle of the first pole from vertical
        theta1_dot:  The angular velocity of the first pole.
        theta2:      The current angle of the second pole from vertical
        theta2_dot:  The angular velocity of the second pole.
    Returns:
        The calculated values for cart acceleration along with angular
        accelerations of both poles.
    """
    # Find the input force direction
    force = (action - 0.5) * FORCE_MAG * 2.0 # action has binary values
    # Calculate projections of forces for the poles
    cos_theta_1     = math.cos(theta1)
    sin_theta_1     = math.sin(theta1)
    g_sin_theta_1   = GRAVITY * sin_theta_1
    cos_theta_2     = math.cos(theta2)
    sin_theta_2     = math.sin(theta2)
    g_sin_theta_2   = GRAVITY * sin_theta_2
    # Calculate intermediate values
    ml_1    = LENGTH_1 * MASS_POLE_1
    ml_2    = LENGTH_2 * MASS_POLE_2
    temp_1  = MUP * theta1_dot / ml_1
    temp_2  = MUP * theta2_dot / ml_2
    fi_1    = (ml_1 * theta1_dot * theta1_dot * sin_theta_1) + \
            (0.75 * MASS_POLE_1 * cos_theta_1 * (temp_1 + g_sin_theta_1))
    fi_2    = (ml_2 * theta2_dot * theta2_dot * sin_theta_2) + \
            (0.75 * MASS_POLE_2 * cos_theta_2 * (temp_2 + g_sin_theta_2))
    mi_1    = MASS_POLE_1 * (1 - (0.75 * cos_theta_1 * cos_theta_1))
    mi_2    = MASS_POLE_2 * (1 - (0.75 * cos_theta_2 * cos_theta_2))
    # Calculate the results: cart acceleration and poles angular accelerations
    x_ddot       = (force + fi_1 + fi_2) / (mi_1 + mi_2 + MASS_CART)
    theta_1_ddot = -0.75 * (x_ddot * cos_theta_1 + g_sin_theta_1 + temp_1) / LENGTH_1
    theta_2_ddot = -0.75 * (x_ddot * cos_theta_2 + g_sin_theta_2 + temp_2) / LENGTH_2

    return x_ddot, theta_1_ddot, theta_2_ddot

def outside_bounds(x, theta1, theta2):
    """
    Function to test whether cart-2-pole system is outside of the
    constraints.
    Arguments:
        action:     The binary action defining direction of
                force to be applied.
        x:          The current cart X position.
        theta1:      The current angle of the first pole from vertical.
        theta2:      The current angle of the second pole from vertical.
    Returns:
        True if system violated constraints, False - otherwise.
    """
    res = x < -2.4 or x > 2.4 or \
        theta1 < -THIRTY_SIX_DEG_IN_RAD or theta1 > THIRTY_SIX_DEG_IN_RAD or \
        theta2 < -THIRTY_SIX_DEG_IN_RAD or theta2 > THIRTY_SIX_DEG_IN_RAD
    return res

def rk4(f, y, dydx, tau):
    """
    The Runge-Kutta fourth order method of numerical approximation of
    the double-pole-cart system dynamics. This function will update
    values in provided list with state variables (y).
    Arguments:
        f:      The current control action 
        y:      The list with current system state variables 
                (x, x_dot, theta1, theta1_dot, theta2, theta2_dot)
        dydx:   The list with derivatives of current state variables
        tau:    The simulation approximation time step size
    """
    hh = tau / 2.0
    yt = [None] * 6
    # update intermediate state
    for i in range(6):
        yt[i] = y[i] + hh * dydx[i]
    # do simulation step
    x_ddot, theta_1_ddot, theta_2_ddot = calc_step(action = f, 
                                                x = yt[0], 
                                                x_dot = yt[1], 
                                                theta1 = yt[2], 
                                                theta1_dot = yt[3], 
                                                theta2 = yt[4], 
                                                theta2_dot = yt[5])
    # store derivatives
    dyt = [yt[1], x_ddot, yt[3], theta_1_ddot, yt[5], theta_2_ddot]

    # update intermediate state 
    for i in range(6):
        yt[i] = y[i] + hh * dyt[i]

    # do one simulation step
    x_ddot, theta_1_ddot, theta_2_ddot = calc_step(action = f, 
                                                x = yt[0], 
                                                x_dot = yt[1], 
                                                theta1 = yt[2], 
                                                theta1_dot = yt[3], 
                                                theta2 = yt[4], 
                                                theta2_dot = yt[5])
    # store derivatives
    dym = [yt[1], x_ddot, yt[3], theta_1_ddot, yt[5], theta_2_ddot]

    # update intermediate state
    for i in range(6):
        yt[i] = y[i] + tau * dym[i]
        dym[i] += dyt[i]

    # do one simulation step
    x_ddot, theta_1_ddot, theta_2_ddot = calc_step(action = f, 
                                                x = yt[0], 
                                                x_dot = yt[1], 
                                                theta1 = yt[2], 
                                                theta1_dot = yt[3], 
                                                theta2 = yt[4], 
                                                theta2_dot = yt[5])
    # store derivatives
    dyt = [yt[1], x_ddot, yt[3], theta_1_ddot, yt[5], theta_2_ddot]

    # find system state after approximation
    h6 = tau / 6.0
    for i in range(6):
        y[i] = y[i] + h6 * (dydx[i] + dyt[i] + 2.0 * dym[i])

def apply_action(action, x, x_dot, theta1, theta1_dot, theta2, theta2_dot, step_number):
    """
    Method to apply the control action to the cart-pole simulation.
    Arguments:
        action:      The binary action defining direction of
                        force to be applied.
        x:           The current cart X position
        x_dot:       The velocity of the cart
        theta1:      The current angle of the first pole from vertical
        theta1_dot:  The angular velocity of the first pole.
        theta2:      The current angle of the second pole from vertical
        theta2_dot:  The angular velocity of the second pole.
        step_number: The current simulation step number
    Returns:
        The updated state.
    """
    # The simulation time step size
    TAU = 0.01

    # The control inputs frequency is two times less than simulation
    # step frequency - hence do two simulation steps
    state = [x, x_dot, theta1, theta1_dot, theta2, theta2_dot] # the state
    dydx = [None] * 6 # the state derivatives holder
    for i in range(2):
        # copy the state derivatives
        dydx[0] = state[1] # x_dot
        dydx[2] = state[3] # theta1_dot
        dydx[4] = state[5] # theta2_dot
        # do one simulation step and store derivatives
        x_ddot, theta_1_ddot, theta_2_ddot = calc_step( action=action, x=x, x_dot=x_dot, 
                                                        theta1=theta1, theta1_dot=theta1_dot, 
                                                        theta2=theta2, theta2_dot=theta2_dot)
        dydx[1] = x_ddot
        dydx[3] = theta_1_ddot
        dydx[5] = theta_2_ddot
        # do Runge-Kutta numerical approximation and update state
        rk4(f=action, y=state, dydx=dydx, tau=TAU)

    # return the updated state values (x, x_dot, theta1, theta1_dot, theta2, theta2_dot)
    return state[0], state[1], state[2], state[3], state[4], state[5]