/*
 * This file contains the implementation that answers EP01's prompt.
 * Together with the code, a test file was submitted. The test file has a
 *  sequence of tests for every algorithm, and, in order to use it, simply
 *  redirect the file to the standard input.
 */

#include <vector>
#include <iostream>
#include <cmath>
#include <string>
#include <ctime>
#include <chrono>

using std::vector;
using std::cout;
using std::cin;

//Simple timer https://gist.github.com/gongzhitaao/7062087
class Timer
{
public:
    Timer() : start{clock::now()} {}
    void reset() { start = clock::now(); }
    double elapsed() const {
        return std::chrono::duration_cast<second_>
            (clock::now() - start).count(); }

private:
    typedef std::chrono::high_resolution_clock clock;
    typedef std::chrono::duration<double, std::ratio<1> > second_;
    std::chrono::time_point<clock> start;
};

// Algorithm 1
double dotproduct (vector<double> x, vector<double> y)
{
    if (x.size() != y.size())
        throw std::runtime_error(
            "Dotproduct is only defined for vector of same lenght\n");
    double max_x = 0.0, max_y = 0.0, dotp = 0.0;
    for (double d : x)
        max_x = std::max(max_x, std::abs(d));
    for (double d : y)
        max_y = std::max(max_y, std::abs(d));
    for (double& d : x)
        d /= max_x;
    for (double& d : y)
        d /= max_y;
    for (int i = 0; i < x.size(); ++i)
        dotp += x[i] * y[i];
    dotp *= max_x * max_y;
    return dotp;
}

// Algorithm 2
double euclidean_norm (vector<double> x)
{
    double max_x = 0.0, sum = 0.0;
    for (double d : x)
        max_x = std::max(max_x, std::abs(d));
    for (double& d : x) {
        d /= max_x;
        sum += d * d;
    }
    return max_x * sqrt(sum);
}

// Algorithm 3 - line-oriented
void matrixvector1 (int n, int m, const vector<double>& A,
                    const vector<double>& x, vector<double>& b)
{
    b.resize(n);
    for (double& el : b) el = 0.0;
    for (int i = 0; i < n; ++i) {
        double mult = 0.0;
        for (int j = 0; j < m; ++j)
            mult += A[i * m + j] * x[j];
        b[i] = mult;
    }
}

// Algorithm 3 = column-oriented
void matrixvector2 (int n, int m, const vector<double>& A,
                    const vector<double>& x, vector<double>& b)
{
    b.resize(n);
    for (double& el : b) el = 0.0;
    for (int j = 0; j < m; ++j)
        for (int i = 0; i < n; ++i)
            b[i] += A[i * m + j] * x[j];
}

// A[n][m] - X[m][p] - B[n][p]
// Algorithm 4 line-oriented
void matrixmatrix1 (int n, int m, int p, const vector<double>& A,
                    const vector<double>& X, vector<double>& B)
{
    B.resize(n * p);
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < p; ++j)
            B[i * p + j] = 0.0;
    for (int i = 0; i < n; ++i)
        for (int k = 0; k < m; ++k)
            for (int j = 0; j < p; ++j)
                B[i * p + j] += A[i * m + k] * X[k * p + j];
}

// Algorithm 4 column-oriented
void matrixmatrix2 (int n, int m, int p, const vector<double>& A,
                    const vector<double>& X, vector<double>& B)
{
    B.resize(n * p);
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < p; ++j)
            B[i * p + j] = 0.0;
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < p; ++j)
            for (int k = 0; k < m; ++k)
                B[i * p + j] += A[i * m + k] * X[k * p + j];
}

void read_vec (int n, vector<double>& vec)
{
    vec.resize(n);
    for (int i = 0; i < n; ++i)
        cin >> vec[i];
}

void read_mat (int n, int m, vector<double>& mat)
{
    mat.resize(n * m);
    for (int i = 0; i < n * m; ++i)
        cin >> mat[i];
}

int main ()
{
    Timer t{};
    vector<double> a, x, y, b, answ, result;
    int numTests, len, n, m, p;
    double differences, time, answer;

    // Tests Alg1
    cin >> numTests;
    cout << "RESULT | ANSWER (NUMPY) | DIFFERENCE\n";
    for (int i = 0; i < numTests; ++i) {
        cin >> len;
        read_vec(len, x);
        read_vec(len, y);
        cin >> answer;
        double resultd = dotproduct(x,y);
        cout << resultd << " - " << answer << " = " << resultd - answer << std::endl;
    }

    // Tests Alg2
    cin >> numTests;
    cout << "RESULT | ANSWER (NUMPY) | DIFFERENCE\n";
    for (int i = 0; i < numTests; ++i) {
        cin >> len;
        read_vec(len, x);
        cin >> answer;
        double resultd = euclidean_norm(x);
        cout << resultd << " - " << answer << " = " << resultd - answer << std::endl;
    }

    // Tests Alg3 + timeit
    cin >> numTests;
    cout << "METHOD | n | m | SUM OF DIFFERENCES | TIME\n";
    for (int i = 0; i < numTests; ++i) {
        cin >> n;
        cin >> m;
        read_mat(n, m, a);
        read_vec(m, x);
        read_vec(n, answ);
        differences = 0.0;
        t.reset();
        matrixvector1(n, m, a, x, result);
        time = t.elapsed();
        for (int i = 0; i < n; ++i)
            differences += std::fabs(answ[i] - result[i]);
        printf(" ONE   | %d | %d |  %lf     | %lf\n", n, m, differences, time);
        differences = 0.0;
        t.reset();
        matrixvector2(n, m, a, x, result);
        time = t.elapsed();
        for (int i = 0; i < n; ++i)
            differences += std::fabs(answ[i] - result[i]);
        printf(" TWO   | %d | %d |  %lf     | %lf\n", n, m, differences, time);
    }

    // Tests Alg4 + timeit
    cin >> numTests;
    cout << "METHOD | n | m | p | SUM OF DIFFERENCES | TIME\n";
    for (int i = 0; i < numTests; ++i) {
        cin >> n;
        cin >> m;
        cin >> p;
        read_mat(n, m, a);
        read_mat(m, p, x);
        read_mat(n, p, answ);
        differences = 0.0;
        t.reset();
        matrixmatrix1(n, m, p, a, x, result);
        time = t.elapsed();
        for (int i = 0; i < n; ++i)
            differences += std::fabs(answ[i] - result[i]);
        printf(" ONE   | %d | %d | %d | %lf     | %lf\n", n, m, p, differences, time);
        differences = 0.0;
        t.reset();
        matrixmatrix2(n, m, p, a, x, result);
        time = t.elapsed();
        for (int i = 0; i < n; ++i)
            differences += std::fabs(answ[i] - result[i]);
        printf(" TWO   | %d | %d | %d |  %lf     | %lf\n", n, m, p, differences, time);
    }

    return 0;
}