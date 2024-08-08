from flask import Flask, request, jsonify, render_template
from scipy.optimize import linprog
import os

app = Flask(__name__)

def solve_lp(c, A, b):
    num_vars = len(c)
    bounds = [(0, None)] * num_vars

    result_min = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')
    result_max = linprog([-coeff for coeff in c], A_ub=A, b_ub=b, bounds=bounds, method='highs')

    if result_min.success and result_max.success:
        return {
            'min_value': result_min.fun,
            'max_value': -result_max.fun  # Since linprog finds the minimum of -f for maximization
        }
    else:
        return {
            'min_value': result_min.fun if result_min.success else None,
            'max_value': -result_max.fun if result_max.success else None,
            'message': result_min.message if not result_min.success else result_max.message
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    
    if 'num_vars' not in data or 'objective' not in data or 'constraints' not in data or 'rhs' not in data:
        return jsonify({
            'error': 'Invalid input. Please provide num_vars, objective, constraints, and rhs in the request body.'
        }), 400

    try:
        num_vars = int(data['num_vars'])
        objective = list(map(float, data['objective'].split()))
        constraints = [list(map(float, c.split())) for c in data['constraints']]
        rhs = list(map(float, data['rhs']))

        if len(objective) != num_vars:
            return jsonify({
                'error': 'The number of variables in the objective function does not match num_vars.'
            }), 400

        if any(len(c) != num_vars for c in constraints):
            return jsonify({
                'error': 'The number of variables in the constraints does not match num_vars.'
            }), 400

    except ValueError as e:
        return jsonify({
            'error': f'Invalid input format: {e}'
        }), 400

    result = solve_lp(objective, constraints, rhs)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
