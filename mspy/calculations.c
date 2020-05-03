#include <stdlib.h>
#include <math.h>
#include <time.h>

#include "Python.h"
#include "arrayobject.h"


typedef struct {
    double *data;
    int len;
    int dim;
    int cell;
} m_arrayd;

typedef struct {
    int *data;
    int len;
    int dim;
    int cell;
} m_arrayi;

typedef struct {
    double minX;
    double maxX;
    double minY;
    double maxY;
} m_box;

typedef struct {
    double level;
    double width;
} m_noise;


#define ELEM_SWAP(a,b) { register double t=(a);(a)=(b);(b)=t; }

void array_print( m_arrayd *p_inarr )
{
    int i, j, len, dim, cell;
    
    len = p_inarr->len;
    dim = p_inarr->dim;
    cell = p_inarr->cell;
    
    // print 1D array
    if ( dim == 1 ) {
        for ( i = 0; i < len; ++i ) {
            printf("%f ", p_inarr->data[i]);
        }
    }
    
    // print 2D array
    else {
        for ( i = 0; i < len; ++i ) {
            for ( j = 0; j < cell; ++j ) {
                printf("%f ", p_inarr->data[i*cell+j]);
            }
            printf("\n");
        }
    }
    
    printf("\n");
}


// BASIC FUNCTIONS
// --------------------------------------------------------------------------

double signal_median(double inarr[], int len)
{
    int low, high;
    int median;
    int middle, ll, hh;
    
    low = 0 ; high = len-1 ; median = (low + high) / 2;
    for ( ; ; ) {
        
        if ( high <= low ) {
            return inarr[median];
        }
        else if ( high == low + 1 ) {
            if ( inarr[low] > inarr[high] ) {
                ELEM_SWAP(inarr[low], inarr[high]);
            }
            return inarr[median];
        }
        
        middle = (low + high) / 2;
        if ( inarr[middle] > inarr[high] )    ELEM_SWAP(inarr[middle], inarr[high]);
        if ( inarr[low] > inarr[high] )       ELEM_SWAP(inarr[low], inarr[high]);
        if ( inarr[middle] > inarr[low] )     ELEM_SWAP(inarr[middle], inarr[low]);
        ELEM_SWAP(inarr[middle], inarr[low+1]) ;
        
        ll = low + 1;
        hh = high;
        for ( ; ; ) {
            do ll++; while ( inarr[low] > inarr[ll] );
            do hh--; while ( inarr[hh] > inarr[low] );
            if ( hh < ll ) {
                break;
            }
            ELEM_SWAP(inarr[ll], inarr[hh]);
        }
        
        ELEM_SWAP(inarr[low], inarr[hh]);
        
        if (hh <= median) {
            low = ll;
        }
        if (hh >= median) {
            high = hh - 1;
        }
    }
}

double signal_interpolate_x( double x1, double y1, double x2, double y2, double y )
{
    double a, b;
    
    if ( x1 == x2 ) {
        return x1;
    }
    
    a = (y2 - y1)/(x2 - x1);
    b = y1 - a * x1;
    
    return ((y - b) / a);
}

double signal_interpolate_y( double x1, double y1, double x2, double y2, double x )
{
    double a, b;
    
    if ( y1 == y2 ) {
        return y1;
    }
    
    a = (y2 - y1)/(x2 - x1);
    b = y1 - a * x1;
    
    return (a*x + b);
}


// SIZE AND POSITION FUNCTIONS
// --------------------------------------------------------------------------

int signal_locate_x( m_arrayd *p_signal, double x )
{
    int lo = 0;
    int hi = p_signal->len;
    int mid;
    
    while ( lo < hi ) {
        mid = ( lo + hi ) / 2;
        if ( x < p_signal->data[mid * p_signal->cell] )
            hi = mid;
        else
            lo = mid + 1;
    }
    
    return lo;
}

int signal_locate_max_y( m_arrayd *p_signal )
{
    int cell, i, idx;
    double value;
    
    cell = p_signal->cell;
    value = p_signal->data[cell-1];
    idx = 0;
    
    for ( i = 0; i < p_signal->len; ++i) {
        if ( p_signal->data[i*cell+cell-1] > value ) {
            value = p_signal->data[i*cell+cell-1];
            idx = i;
        }
    }
    
    return idx;
}

m_box signal_box( m_arrayd *p_signal )
{
    m_box box;
    double y;
    int i;
    
    box.minX = p_signal->data[0];
    box.maxX = p_signal->data[2*p_signal->len-2];
    
    box.minY = p_signal->data[1];
    box.maxY = p_signal->data[1];
    
    for ( i = 0; i < p_signal->len; ++i ) {
        y = p_signal->data[i*2+1];
        if ( y < box.minY ) {
            box.minY = y;
        }
        if ( y > box.maxY ) {
            box.maxY = y;
        }
    }
    
    return box;
}


// PEAK-RELATED FUNCTIONS
// --------------------------------------------------------------------------

double signal_intensity( m_arrayd *p_signal, double x )
{
    int idx;
    double y, x1, x2, y1, y2;
    
    // locate x-value
    idx = signal_locate_x( p_signal, x );
    if ( idx == 0 || idx == p_signal->len ) {
        return 0;
    }
    
    // interpolate y-value
    x1 = p_signal->data[2*idx-2];
    y1 = p_signal->data[2*idx-1];
    x2 = p_signal->data[2*idx];
    y2 = p_signal->data[2*idx+1];
    y = signal_interpolate_y( x1, y1, x2, y2, x );
    
    return y;
}

double signal_centroid( m_arrayd *p_signal, double x, double height )
{
    int idx, ileft, iright;
    double xleft, xright;
    double x1, x2, y1, y2;
    
    // locate x-value
    idx = signal_locate_x( p_signal, x );
    if ( idx == 0 || idx == p_signal->len ) {
        return 0;
    }
    
    // get left index
    ileft = idx-1;
    while ( ( ileft > 0 ) && ( p_signal->data[2*ileft+1] > height ) ) {
        --ileft;
    }
    
    // get right index
    iright = idx;
    while ( ( ileft < p_signal->len-1 ) && ( p_signal->data[2*iright+1] > height ) ) {
        ++iright;
    }
    
    // check indexes
    if ( ileft == iright ) {
        return p_signal->data[2*ileft];
    }
    
    // interpolate y-values
    x1 = p_signal->data[2*ileft];
    y1 = p_signal->data[2*ileft+1];
    x2 = p_signal->data[2*ileft+2];
    y2 = p_signal->data[2*ileft+3];
    xleft = signal_interpolate_x( x1, y1, x2, y2, height );
    
    x1 = p_signal->data[2*iright-2];
    y1 = p_signal->data[2*iright-1];
    x2 = p_signal->data[2*iright];
    y2 = p_signal->data[2*iright+1];
    xright = signal_interpolate_x( x1, y1, x2, y2, height );
    
    return ((xleft + xright) / 2);
}

double signal_width( m_arrayd *p_signal, double x, double height )
{
    int idx, ileft, iright;
    double xleft, xright;
    double x1, x2, y1, y2;
    
    // locate x-value
    idx = signal_locate_x( p_signal, x );
    if ( idx == 0 || idx == p_signal->len ) {
        return 0;
    }
    
    // get left index
    ileft = idx - 1;
    while ( ( ileft > 0 ) && ( p_signal->data[2*ileft+1] > height ) ) {
        --ileft;
    }
    
    // get right index
    iright = idx;
    while ( ( iright < p_signal->len-1 ) && ( p_signal->data[2*iright+1] > height ) ) {
        ++iright;
    }
    
    // check indexes
    if ( ileft == iright ) {
        return 0;
    }
    
    // interpolate y-values
    x1 = p_signal->data[2*ileft];
    y1 = p_signal->data[2*ileft+1];
    x2 = p_signal->data[2*ileft+2];
    y2 = p_signal->data[2*ileft+3];
    xleft = signal_interpolate_x( x1, y1, x2, y2, height );
    
    x1 = p_signal->data[2*iright-2];
    y1 = p_signal->data[2*iright-1];
    x2 = p_signal->data[2*iright];
    y2 = p_signal->data[2*iright+1];
    xright = signal_interpolate_x( x1, y1, x2, y2, height );
    
    return fabs(xright - xleft);
}

double signal_area( m_arrayd *p_signal )
{
    double area;
    double x1, x2, y1, y2;
    int i;
    
    // check points
    if ( p_signal->len < 2) {
        return 0;
    }
    
    // calculate area
    area = 0.0;
    for ( i = 1; i < p_signal->len; ++i ) {
        x1 = p_signal->data[i*2-2];
        y1 = p_signal->data[i*2-1];
        x2 = p_signal->data[i*2];
        y2 = p_signal->data[i*2+1];
        area += (y1*(x2-x1)) + ((y2-y1)*(x2-x1)/2);
    }
    
    return area;
}

m_noise signal_noise( m_arrayd *p_signal )
{
    m_noise noise;
    double *p_buff;
    int i;
    
    // init noise
    noise.level = 0;
    noise.width = 0;
    
    // make intensities buffer
    if ( (p_buff = (double*) malloc( p_signal->len*sizeof(double)) ) == NULL ) {
        return noise;
    }
    for ( i = 0; i < p_signal->len; ++i ) {
        p_buff[i] = p_signal->data[2*i+1];
    }
    
    // find noise level (median of y-values)
    noise.level = signal_median( p_buff, p_signal->len );
    
    // calculate abs deviations
    for ( i = 0; i < p_signal->len; ++i ) {
        p_buff[i] = fabs(p_buff[i] - noise.level);
    }
    
    // calculate noise width (median of abs deviations)
    noise.width = signal_median( p_buff, p_signal->len );
    noise.width *= 2;
    
    // free buffer
    free(p_buff);
    
    return noise;
}

m_arrayd *signal_local_maxima( m_arrayd *p_signal )
{
    m_arrayd *p_maxima;
    double *p_buff;
    double currentX, currentY;
    int size, count, rising;
    int i;
    
    // init buffer
    size = (int) (p_signal->len/2 + 1);
    if ( (p_buff = (double*) malloc( 2*size*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    
    // find maxima
    rising = 0;
    count = 0;
    currentX = p_signal->data[0];
    currentY = p_signal->data[1];
    
    for ( i = 0; i < p_signal->len; ++i ) {
        
        if ( p_signal->data[2*i+1] > currentY ) {
            rising = 1;
        }
        else if ( p_signal->data[2*i+1] < currentY && rising ) {
            p_buff[2*count] = currentX;
            p_buff[2*count+1] = currentY;
            rising = 0;
            ++count;
        }
        
        currentX = p_signal->data[2*i];
        currentY = p_signal->data[2*i+1];
    }
    
    // init maxima
    if ( (p_maxima = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_maxima->data = (double*) malloc( 2*count*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_maxima->len = count;
    p_maxima->dim = 2;
    p_maxima->cell = 2;
    
    // copy data
    for ( i = 0; i < count; ++i ) {
        p_maxima->data[2*i] = p_buff[2*i];
        p_maxima->data[2*i+1] = p_buff[2*i+1];
    }
    
    // free buffer
    free(p_buff);
    
    return p_maxima;
}


// SIGNAL OPERATIONS
// --------------------------------------------------------------------------

m_arrayd *signal_crop( m_arrayd *p_signal, double minX, double maxX )
{
    m_arrayd *p_result;
    int idx1, idx2;
    int size, count;
    double x1, x2, y1, y2;
    int i;
    
    // get indexes of limits
    idx1 = signal_locate_x(p_signal, minX);
    idx2 = signal_locate_x(p_signal, maxX);
    
    // get size of result
    size = idx2 - idx1;
    if (idx1 > 0) ++size;
    if (idx2 > 0 && idx2 < p_signal->len && p_signal->data[2*(idx2-1)] != maxX) ++size;
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*size*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = size;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // init counter
    count = 0;
    
    // interpolate left edge
    if ( idx1 > 0 ) {
        x1 = p_signal->data[idx1*2-2];
        y1 = p_signal->data[idx1*2-1];
        x2 = p_signal->data[idx1*2];
        y2 = p_signal->data[idx1*2+1];
        p_result->data[0] = minX;
        p_result->data[1] = signal_interpolate_y( x1, y1, x2, y2, minX );
        ++count;
    }
    
    // add inner points
    for ( i = idx1; i < idx2; ++i) {
        p_result->data[count*2] = p_signal->data[i*2];
        p_result->data[count*2+1] = p_signal->data[i*2+1];
        ++count;
    }
    
    // interpolate right edge
    if ( idx2 > 0 && idx2 < p_signal->len && p_signal->data[2*(idx2-1)] != maxX ) {
        x1 = p_signal->data[idx2*2-2];
        y1 = p_signal->data[idx2*2-1];
        x2 = p_signal->data[idx2*2];
        y2 = p_signal->data[idx2*2+1];
        p_result->data[count*2] = maxX;
        p_result->data[count*2+1] = signal_interpolate_y( x1, y1, x2, y2, maxX );
        ++count;
    }
    
    return p_result;
}

m_arrayd *signal_offset( m_arrayd *p_signal, double x, double y )
{
    m_arrayd *p_result;
    int i;
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*p_signal->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = p_signal->len;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // offset signal
    for ( i = 0; i < p_signal->len; ++i) {
        p_result->data[i*2] = p_signal->data[i*2] + x;
        p_result->data[i*2+1] = p_signal->data[i*2+1] + y;
    }
    
    return p_result;
}

m_arrayd *signal_multiply( m_arrayd *p_signal, double x, double y )
{
    m_arrayd *p_result;
    int i;
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*p_signal->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = p_signal->len;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // multiply signal
    for ( i = 0; i < p_signal->len; ++i) {
        p_result->data[i*2] = p_signal->data[i*2] * x;
        p_result->data[i*2+1] = p_signal->data[i*2+1] * y;
    }
    
    return p_result;
}

m_arrayd *signal_normalize( m_arrayd *p_signal )
{
    m_arrayd *p_result;
    double maxY;
    int i;
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*p_signal->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = p_signal->len;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // get max Y
    maxY = p_signal->data[1];
    for ( i = 0; i < p_signal->len; ++i ) {
        maxY = ( p_signal->data[i*2+1] > maxY ) ? p_signal->data[i*2+1] : maxY;
    }
    
    // normalize signal
    for ( i = 0; i < p_signal->len; ++i) {
        p_result->data[i*2] = p_signal->data[i*2];
        p_result->data[i*2+1] = p_signal->data[i*2+1] / maxY;
    }
    
    return p_result;
}

m_arrayd *signal_smooth_ma( m_arrayd *p_signal, int window, int cycles )
{
    m_arrayd *p_result;
    double average, ksum;
    int ksize;
    int c, i, j, idx;
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*p_signal->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = p_signal->len;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // check window size
    if ( window > p_signal->len ) {
        window = p_signal->len;
    }
    
    // make window even
    if ( window % 2 != 0) {
        window -= 1;
    }
    
    // make kernel
    ksize = window + 1;
    ksum = window + 1;
    double kernel[ksize];
    for ( i = 0; i <= ksize; ++i ) {
        kernel[i] = 1/ksum;
    }
    
    // smooth cycles
    for ( c = 0; c < cycles; ++c ) {
        
        // get average in window for every point
        for ( i = 0; i < p_signal->len; ++i ) {
            
            average = 0.0;
            for ( j = 0; j <= window; ++j ) {
                idx = (int) fabs(i+j-window/2);
                if ( idx >= p_signal->len) {
                    idx -= 2*(idx - p_signal->len + 1);
                }
                average += kernel[j] * p_signal->data[2*idx+1];
            }
            
            p_result->data[2*i] = p_signal->data[2*i];
            p_result->data[2*i+1] = average;
        }
    }
    
    return p_result;
}

m_arrayd *signal_smooth_ga( m_arrayd *p_signal, int window, int cycles )
{
    m_arrayd *p_result;
    double average, ksum, r, k;
    int ksize;
    int c, i, j, idx;
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*p_signal->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = p_signal->len;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // check window size
    if ( window > p_signal->len ) {
        window = p_signal->len;
    }
    
    // make window even
    if ( window % 2 != 0) {
        window -= 1;
    }
    
    // make kernel
    ksize = window + 1;
    ksum = 0;
    double kernel[ksize];
    for ( i = 0; i <= ksize; ++i ) {
        r = (i - (ksize-1)/2.0);
        k = exp(-(r*r/(ksize*ksize/16.0)));
        kernel[i] = k;
        ksum += k;
    }
    for ( i = 0; i <= ksize; ++i ) {
        kernel[i] /= ksum;
    }
    
    // smooth cycles
    for ( c = 0; c < cycles; ++c ) {
        
        // get weighted average in window for every point
        for ( i = 0; i < p_signal->len; ++i ) {
            
            average = 0.0;
            for ( j = 0; j <= window; ++j ) {
                idx = (int) fabs(i+j-window/2);
                if ( idx >= p_signal->len) {
                    idx -= 2*(idx - p_signal->len + 1);
                }
                average += kernel[j] * p_signal->data[2*idx+1];
            }
            
            p_result->data[2*i] = p_signal->data[2*i];
            p_result->data[2*i+1] = average;
        }
    }
    
    return p_result;
}

m_arrayd *signal_combine( m_arrayd *p_signalA, m_arrayd *p_signalB )
{
    m_arrayd *p_result;
    double *p_buff;
    double x1, x2, y1, y2;
    int lenA, lenB, count;
    int i, j;
    
    // init buffer
    lenA = p_signalA->len;
    lenB = p_signalB->len;
    if ( (p_buff = (double*) malloc( 2*(lenA+lenB)*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    
    // init counters
    i = 0;
    j = 0;
    count = 0;
    
    while ( i < lenA || j < lenB ) {
        
        // process points within both arrays
        if ( i < lenA && j < lenB ) {
            
            // add interpolated point from B
            if ( p_signalA->data[i*2] < p_signalB->data[j*2] ) {
                p_buff[count*2] = p_signalA->data[i*2];
                p_buff[count*2+1] = p_signalA->data[i*2+1];
                if ( j > 0) {
                    x1 = p_signalB->data[j*2-2];
                    y1 = p_signalB->data[j*2-1];
                    x2 = p_signalB->data[j*2];
                    y2 = p_signalB->data[j*2+1];
                    p_buff[count*2+1] += signal_interpolate_y( x1, y1, x2, y2, p_signalA->data[i*2]);
                }
                ++i;
            }
            
            // add interpolated point from A
            else if ( p_signalA->data[i*2] > p_signalB->data[j*2] ) {
                p_buff[count*2] = p_signalB->data[j*2];
                p_buff[count*2+1] = p_signalB->data[j*2+1];
                if ( i > 0) {
                    x1 = p_signalA->data[i*2-2];
                    y1 = p_signalA->data[i*2-1];
                    x2 = p_signalA->data[i*2];
                    y2 = p_signalA->data[i*2+1];
                    p_buff[count*2+1] += signal_interpolate_y( x1, y1, x2, y2, p_signalB->data[j*2]);
                }
                ++j;
            }
            
            // add same point
            else {
                p_buff[count*2] = p_signalA->data[i*2];
                p_buff[count*2+1] = p_signalA->data[i*2+1] + p_signalB->data[j*2+1];
                ++i;
                ++j;
            }
        }
        
        // process additional points from array A
        else if ( i < lenA ) {
            p_buff[count*2] = p_signalA->data[i*2];
            p_buff[count*2+1] = p_signalA->data[i*2+1];
            ++i;
        }
        
        // process additional points from array B
        else if ( j < lenB ) {
            p_buff[count*2] = p_signalB->data[j*2];
            p_buff[count*2+1] = p_signalB->data[j*2+1];
            ++j;
        }
        
        ++count;
    }
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*count*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = count;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // copy points
    for ( i = 0; i < count; ++i) {
        p_result->data[i*2] = p_buff[i*2];
        p_result->data[i*2+1] = p_buff[i*2+1];
    }
    
    // free buffer
    free(p_buff);
    
    return p_result;
}

m_arrayd *signal_overlay( m_arrayd *p_signalA, m_arrayd *p_signalB )
{
    m_arrayd *p_result;
    double *p_buff;
    double y, x1, x2, y1, y2;
    int lenA, lenB, count;
    int i, j;
    
    // init buffer
    lenA = p_signalA->len;
    lenB = p_signalB->len;
    if ( (p_buff = (double*) malloc( 2*(lenA+lenB)*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    
    // init counters
    i = 0;
    j = 0;
    count = 0;
    
    while ( i < lenA || j < lenB ) {
        
        // process points within both arrays
        if ( i < lenA && j < lenB ) {
            
            // add interpolated point from B
            if ( p_signalA->data[i*2] < p_signalB->data[j*2] ) {
                p_buff[count*2] = p_signalA->data[i*2];
                p_buff[count*2+1] = p_signalA->data[i*2+1];
                if ( j > 0) {
                    x1 = p_signalB->data[j*2-2];
                    y1 = p_signalB->data[j*2-1];
                    x2 = p_signalB->data[j*2];
                    y2 = p_signalB->data[j*2+1];
                    y = signal_interpolate_y( x1, y1, x2, y2, p_signalA->data[i*2]);
                    p_buff[count*2+1] = ( p_signalA->data[i*2+1] > y ) ? p_signalA->data[i*2+1] : y;
                }
                ++i;
            }
            
            // add interpolated point from A
            else if ( p_signalA->data[i*2] > p_signalB->data[j*2] ) {
                p_buff[count*2] = p_signalB->data[j*2];
                p_buff[count*2+1] = p_signalB->data[j*2+1];
                if ( i > 0) {
                    x1 = p_signalA->data[i*2-2];
                    y1 = p_signalA->data[i*2-1];
                    x2 = p_signalA->data[i*2];
                    y2 = p_signalA->data[i*2+1];
                    y = signal_interpolate_y( x1, y1, x2, y2, p_signalB->data[j*2]);
                    p_buff[count*2+1] = ( p_signalB->data[j*2+1] > y ) ? p_signalB->data[j*2+1] : y;
                }
                ++j;
            }
            
            // add same point
            else {
                p_buff[count*2] = p_signalA->data[i*2];
                p_buff[count*2+1] = ( p_signalA->data[i*2+1] > p_signalB->data[j*2+1]) ? p_signalA->data[i*2+1] : p_signalB->data[j*2+1];
                ++i;
                ++j;
            }
        }
        
        // process additional points from array A
        else if ( i < lenA ) {
            p_buff[count*2] = p_signalA->data[i*2];
            p_buff[count*2+1] = p_signalA->data[i*2+1];
            ++i;
        }
        
        // process additional points from array B
        else if ( j < lenB ) {
            p_buff[count*2] = p_signalB->data[j*2];
            p_buff[count*2+1] = p_signalB->data[j*2+1];
            ++j;
        }
        
        ++count;
    }
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*count*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = count;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // copy points
    for ( i = 0; i < count; ++i) {
        p_result->data[i*2] = p_buff[i*2];
        p_result->data[i*2+1] = p_buff[i*2+1];
    }
    
    // free buffer
    free(p_buff);
    
    return p_result;
}

m_arrayd *signal_subtract( m_arrayd *p_signalA, m_arrayd *p_signalB )
{
    m_arrayd *p_result;
    double *p_buff;
    double x1, x2, y1, y2;
    int lenA, lenB, count;
    int i, j;
    
    // init buffer
    lenA = p_signalA->len;
    lenB = p_signalB->len;
    if ( (p_buff = (double*) malloc( 2*(lenA+lenB)*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    
    // init counters
    i = 0;
    j = 0;
    count = 0;
    
    while ( i < lenA || j < lenB ) {
        
        // process points within both arrays
        if ( i < lenA && j < lenB ) {
            
            // add interpolated point from B
            if ( p_signalA->data[i*2] < p_signalB->data[j*2] ) {
                p_buff[count*2] = p_signalA->data[i*2];
                p_buff[count*2+1] = p_signalA->data[i*2+1];
                if ( j > 0) {
                    x1 = p_signalB->data[j*2-2];
                    y1 = p_signalB->data[j*2-1];
                    x2 = p_signalB->data[j*2];
                    y2 = p_signalB->data[j*2+1];
                    p_buff[count*2+1] -= signal_interpolate_y( x1, y1, x2, y2, p_signalA->data[i*2]);
                }
                ++i;
            }
            
            // add interpolated point from A
            else if ( p_signalA->data[i*2] > p_signalB->data[j*2] ) {
                p_buff[count*2] = p_signalB->data[j*2];
                p_buff[count*2+1] = -p_signalB->data[j*2+1];
                if ( i > 0) {
                    x1 = p_signalA->data[i*2-2];
                    y1 = p_signalA->data[i*2-1];
                    x2 = p_signalA->data[i*2];
                    y2 = p_signalA->data[i*2+1];
                    p_buff[count*2+1] += signal_interpolate_y( x1, y1, x2, y2, p_signalB->data[j*2]);
                }
                ++j;
            }
            
            // add same point
            else {
                p_buff[count*2] = p_signalA->data[i*2];
                p_buff[count*2+1] = p_signalA->data[i*2+1] - p_signalB->data[j*2+1];
                ++i;
                ++j;
            }
        }
        
        // process additional points from array A
        else if ( i < lenA ) {
            p_buff[count*2] = p_signalA->data[i*2];
            p_buff[count*2+1] = p_signalA->data[i*2+1];
            ++i;
        }
        
        // process additional points from array B
        else if ( j < lenB ) {
            p_buff[count*2] = p_signalB->data[j*2];
            p_buff[count*2+1] = -p_signalB->data[j*2+1];
            ++j;
        }
        
        ++count;
    }
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*count*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = count;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // copy points
    for ( i = 0; i < count; ++i) {
        p_result->data[i*2] = p_buff[i*2];
        p_result->data[i*2+1] = p_buff[i*2+1];
    }
    
    // free buffer
    free(p_buff);
    
    return p_result;
}

m_arrayd *signal_subbase( m_arrayd *p_signal, m_arrayd *p_baseline )
{
    m_arrayd *p_result;
    double a, b;
    int i, j;
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*p_signal->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = p_signal->len;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // copy signal points
    for ( i = 0; i < p_signal->len; ++i ) {
        p_result->data[2*i] = p_signal->data[2*i];
        p_result->data[2*i+1] = p_signal->data[2*i+1];
    }
    
    // check baseline
    if ( p_baseline->len == 0 ) {
        return p_result;
    }
    
    // apply single-point baseline
    else if ( p_baseline->len == 1 ) {
        for ( i = 0; i < p_signal->len; ++i ) {
            p_result->data[2*i+1] -= p_baseline->data[1];
        }
    }
    
    // multiple point baseline
    else {
        
        // get first baseline segment
        j = 1;
        a = (p_baseline->data[2*j+1] - p_baseline->data[2*j-2+1]) / (p_baseline->data[2*j] - p_baseline->data[2*j-2]);
        b = p_baseline->data[2*j-2+1] - a * p_baseline->data[2*j-2];
        
        // shift data
        for ( i = 0; i < p_signal->len; ++i ) {
            
            // get new baseline segment
            if ( (p_signal->data[2*i] > p_baseline->data[2*j]) && (j < p_baseline->len-1) ) {
                j++;
                a = (p_baseline->data[2*j+1] - p_baseline->data[2*j-2+1]) / (p_baseline->data[2*j] - p_baseline->data[2*j-2]);
                b = p_baseline->data[2*j-2+1] - a * p_baseline->data[2*j-2];
            }
            
            p_result->data[2*i+1] -= a * p_signal->data[2*i] + b;
        }
    }
    
    // clip negative y-values
    for ( i = 0; i < p_signal->len; ++i ) {
        if (p_result->data[2*i+1] < 0) {
            p_result->data[2*i+1] = 0;
        }
    }
    
    return p_result;
}


// PLOT FUNCTIONS
// --------------------------------------------------------------------------

m_arrayd *signal_rescale( m_arrayd *p_signal, double scaleX, double scaleY, double shiftX, double shiftY )
{
    m_arrayd *p_result;
    int i;
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*p_signal->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = p_signal->len;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // multiply points
    for ( i = 0; i < p_signal->len; ++i) {
        p_result->data[i*2] = round(p_signal->data[i*2] * scaleX + shiftX);
        p_result->data[i*2+1] = round(p_signal->data[i*2+1] * scaleY + shiftY);
    }
    
    return p_result;
}

m_arrayd *signal_filter( m_arrayd *p_signal, double resol )
{
    m_arrayd *p_result;
    double *p_buff;
    double currentX, currentY, lastX, previousX, previousY, minY, maxY;
    int i, count;
    
    // init buffer
    if ( (p_buff = (double*) malloc( 4*2*p_signal->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    
    // add first point
    p_buff[0] = p_signal->data[0];
    p_buff[1] = p_signal->data[1];
    lastX = previousX = p_signal->data[0];
    minY = maxY = previousY = p_signal->data[1];
    count = 1;
    
    // filter points
    for ( i = 1; i < p_signal->len; i++ ) {
        currentX = p_signal->data[2*i];
        currentY = p_signal->data[2*i+1];
        
        // if difference between current and previous x-values is higher
        //than resolution save previous point and its minimum and maximum
        if ( (currentX-lastX) >= resol || i == (p_signal->len-1) ) {
            
            // add minimum in range
            if ( p_buff[2*count-2] != lastX || p_buff[2*count-1] != minY ) {
                p_buff[2*count] = lastX;
                p_buff[2*count+1] = minY;
                ++count;
            }
            
            // add maximum in range
            if ( maxY != minY ) {
                p_buff[2*count] = lastX;
                p_buff[2*count+1] = maxY;
                ++count;
            }
            
            // add last point in range
            if ( previousY != maxY) {
                p_buff[2*count] = previousX;
                p_buff[2*count+1] = previousY;
                ++count;
            }
            
            // add current point
            p_buff[2*count] = currentX;
            p_buff[2*count+1] = currentY;
            ++count;
            
            lastX = previousX = currentX;
            maxY = minY = previousY = currentY;
        }
        
        // if difference between current and previous x-values is lower
        // than resolution remember minimum and maximum
        else {
            minY = ( currentY < minY ) ? currentY : minY;
            maxY = ( currentY > maxY ) ? currentY : maxY;
            previousX = currentX;
            previousY = currentY;
        }
    }
    
    
    // init results
    if ( (p_result = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (double*) malloc( 2*count*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = count;
    p_result->dim = 2;
    p_result->cell = 2;
    
    // copy points
    for ( i = 0; i < count; ++i) {
        p_result->data[i*2] = p_buff[i*2];
        p_result->data[i*2+1] = p_buff[i*2+1];
    }
    
    // free buffer
    free(p_buff);
    
    return p_result;
}


// SIGNAL MODELLING
// --------------------------------------------------------------------------

m_arrayd *signal_gaussian( double x, double minY, double maxY, double fwhm, int points )
{
    m_arrayd *p_profile;
    double minX, maxX, step;
    double amplitude, f;
    double currentX;
    int i;
    
    // init profile
    if ( (p_profile = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_profile->data = (double*) malloc( 2*points*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_profile->len = points;
    p_profile->dim = 2;
    p_profile->cell = 2;
    
    // get range, step and amplitude
    minX = x - (5*fwhm);
    maxX = x + (5*fwhm);
    step = (maxX - minX) / points;
    amplitude = maxY - minY;
    
    // make data
    f = (fwhm / 1.66)*(fwhm / 1.66);
    currentX = minX;
    for ( i = 0; i < points; ++i ) {
        p_profile->data[2*i] = currentX;
        p_profile->data[2*i+1] = minY + amplitude * exp( -((currentX-x)*(currentX-x)) / f );
        currentX += step;
    }
    
    return p_profile;
}

m_arrayd *signal_lorentzian( double x, double minY, double maxY, double fwhm, int points )
{
    m_arrayd *p_profile;
    double minX, maxX, step;
    double amplitude, f;
    double currentX;
    int i;
    
    // init profile
    if ( (p_profile = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_profile->data = (double*) malloc( 2*points*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_profile->len = points;
    p_profile->dim = 2;
    p_profile->cell = 2;
    
    // get range, step and amplitude
    minX = x - (10*fwhm);
    maxX = x + (10*fwhm);
    step = (maxX - minX) / points;
    amplitude = maxY - minY;
    
    // make data
    f = (fwhm / 2.0)*(fwhm / 2.0);
    currentX = minX;
    for ( i = 0; i < points; ++i ) {
        p_profile->data[2*i] = currentX;
        p_profile->data[2*i+1] = minY + amplitude / ( 1.0  + ((currentX-x)*(currentX-x)) / f );
        currentX += step;
    }
    
    return p_profile;
}

m_arrayd *signal_gausslorentzian( double x, double minY, double maxY, double fwhm, int points )
{
    m_arrayd *p_profile;
    double minX, maxX, step;
    double amplitude, f;
    double currentX;
    int i;
    
    // init profile
    if ( (p_profile = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_profile->data = (double*) malloc( 2*points*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_profile->len = points;
    p_profile->dim = 2;
    p_profile->cell = 2;
    
    // get range, step and amplitude
    minX = x - (5*fwhm);
    maxX = x + (10*fwhm);
    step = (maxX - minX) / points;
    amplitude = maxY - minY;
    
    // make gaussian part
    f = (fwhm / 1.66)*(fwhm / 1.66);
    currentX = minX;
    for ( i = 0; i < points; ++i ) {
        p_profile->data[2*i] = currentX;
        p_profile->data[2*i+1] = minY + amplitude * exp( -((currentX-x)*(currentX-x)) / f );
        currentX += step;
        if ( currentX >= x ) break;
    }
    
    // make lorentzian part
    f = (fwhm / 2.0)*(fwhm / 2.0);
    for ( ; i < points; ++i ) {
        p_profile->data[2*i] = currentX;
        p_profile->data[2*i+1] = minY + amplitude / ( 1.0  + ((currentX-x)*(currentX-x)) / f );
        currentX += step;
    }
    
    return p_profile;
}

m_arrayd *signal_profile_raster( m_arrayd *p_peaks, int points )
{
    
    m_arrayd *p_raster;
    double *p_buff;
    double minX, maxX, minFwhm, maxFwhm;
    double a, b, x;
    int size, count, i;
    
    // get ranges
    minX = maxX = p_peaks->data[0];
    minFwhm = maxFwhm = p_peaks->data[2];
    for ( i = 0; i < p_peaks->len; ++i) {
        minX = ( p_peaks->data[3*i] < minX ) ? p_peaks->data[3*i] : minX;
        maxX = ( p_peaks->data[3*i] > maxX ) ? p_peaks->data[3*i] : maxX;
        minFwhm = ( p_peaks->data[3*i+2] < minFwhm ) ? p_peaks->data[3*i+2] : minFwhm;
        maxFwhm = ( p_peaks->data[3*i+2] > maxFwhm ) ? p_peaks->data[3*i+2] : maxFwhm;
    }
    
    // extend ranges
    minX -= 5*maxFwhm;
    maxX += 5*maxFwhm;
    
    // get max raster size
    size = (int) ((maxX - minX) / (minFwhm / points));
    
    // make linear gradient
    a = ( maxFwhm/points - minFwhm/points ) / ( maxX - minX );
    b = minFwhm/points - a * minX;
    
    // init buffer
    if ( (p_buff = (double*) malloc( size*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    
    // calc raster
    count = 0;
    x = minX;
    while ( x < maxX && count < size ) {
        p_buff[count] = x;
        x += a*x + b;
        ++count;
    }
    
    // init final raster
    if ( (p_raster = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_raster->data = (double*) malloc( count*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_raster->len = count;
    p_raster->dim = 1;
    p_raster->cell = 1;
    
    // make raster
    for ( i = 0; i < count; ++i) {
        p_raster->data[i] = p_buff[i];
    }
    
    // free buffer
    free(p_buff);
    
    return p_raster;
}

m_arrayd *signal_profile_to_raster( m_arrayd *p_peaks, m_arrayd *p_raster, double noise, int shape )
{
    
    m_arrayd *p_profile;
    double mz, intens, fwhm, f, minX, maxX;
    int idx1, idx2;
    int i, j;
    
    // check input
    if ( p_peaks->len == 0 || p_raster->len == 0) {
        return NULL;
    }
    
    // init profile
    if ( (p_profile = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_profile->data = (double*) malloc( 2*p_raster->len*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_profile->len = p_raster->len;
    p_profile->dim = 2;
    p_profile->cell = 2;
    for ( i = 0; i < p_raster->len; ++i) {
        p_profile->data[2*i] = p_raster->data[i];
        p_profile->data[2*i+1] = 0;
    }
    
    // model peaks
    for ( i = 0; i < p_peaks->len; ++i ) {
        
        mz = p_peaks->data[3*i];
        intens = p_peaks->data[3*i+1];
        fwhm = p_peaks->data[3*i+2];
        
        // model peaks as gaussians
        if ( shape == 0) {
            
            minX = mz - (5*fwhm);
            maxX = mz + (5*fwhm);
            idx1 = signal_locate_x( p_profile, minX);
            idx2 = signal_locate_x( p_profile, maxX);
            
            f = (fwhm / 1.66)*(fwhm / 1.66);
            for ( j = idx1; j < idx2; ++j ) {
                p_profile->data[2*j+1] += intens * exp( -(p_profile->data[2*j]-mz)*(p_profile->data[2*j]-mz) / f );
            }
        }
        
        // model peak as lorentzians
        else if ( shape == 1) {
            
            minX = mz - (10*fwhm);
            maxX = mz + (10*fwhm);
            idx1 = signal_locate_x( p_profile, minX);
            idx2 = signal_locate_x( p_profile, maxX);
            
            f = (fwhm / 2.0)*(fwhm / 2.0);
            for ( j = idx1; j < idx2; ++j ) {
                p_profile->data[2*j+1] += intens / ( 1.0  + ((p_profile->data[2*j]-mz)*(p_profile->data[2*j]-mz)) / f );
            }
        }
        
        // model peak as half-gaussians half-lorentzians
        else if ( shape == 2) {
            
            minX = mz - (5*fwhm);
            maxX = mz + (10*fwhm);
            idx1 = signal_locate_x( p_profile, minX);
            idx2 = signal_locate_x( p_profile, maxX);
            
            // model gaussian part
            f = (fwhm / 1.66)*(fwhm / 1.66);
            for ( j = idx1; j < idx2; ++j ) {
                p_profile->data[2*j+1] += intens * exp( -(p_profile->data[2*j]-mz)*(p_profile->data[2*j]-mz) / f );
                if ( p_profile->data[2*j] >= mz ) break;
            }
            
            // model lorentzian part
            f = (fwhm / 2.0)*(fwhm / 2.0);
            for ( j++; j < idx2; ++j ) {
                p_profile->data[2*j+1] += intens / ( 1.0  + ((p_profile->data[2*j]-mz)*(p_profile->data[2*j]-mz)) / f );
            }
        }
        
        // unknown model
        else {
            return NULL;
        }
    }
    
    // add noise
    if ( noise != 0 ) {
        srand( (unsigned) time(0) );
        for ( i = 0; i < p_profile->len; ++i ) {
            p_profile->data[2*i+1] += noise * (double) rand() / (double) (RAND_MAX) - noise/2;
        }
    }
    
    return p_profile;
}

m_arrayd *signal_profile( m_arrayd *p_peaks, int points, double noise, int shape )
{
    
    m_arrayd *p_profile, *p_raster;
    
    // make raster
    p_raster = signal_profile_raster( p_peaks, points );
    if ( p_raster == NULL ) {
        return NULL;
    }
    
    // make profile
    p_profile = signal_profile_to_raster( p_peaks, p_raster, noise, shape );
    if ( p_profile == NULL ) {
        return NULL;
    }
    
    // free raster
    free(p_raster->data);
    free(p_raster);
    
    return p_profile;
}


// COMPOSITION GENERATOR
// --------------------------------------------------------------------------

void formula_generator( m_arrayi *p_result, int elcount, int minimum[], int maximum[], double masses[], double loMass, double hiMass, int limit, int pos)
{
    int *current;
    double mass;
    int i;
    
    // calculate current mass
    mass = 0;
    for ( i = 0; i < elcount; ++i) {
        mass += minimum[i]*masses[i];
    }
    
    // recursion end reached
    if ( pos == elcount ) {
        
        // check mass tolerance and store current composition
        if ( (mass >= loMass) && (mass <= hiMass) && (p_result->len < limit) ) {
            for ( i = 0; i < elcount; ++i) {
                p_result->data[p_result->len*elcount+i] = minimum[i];
            }
            p_result->len++;
        }
        return;
    }
    
    // duplicate current minima as a new item to allow changes
    if ( (current = (int*) malloc( elcount*sizeof(int)) ) == NULL ) {
        return;
    }
    for ( i = 0; i < elcount; ++i) {
        current[i] = minimum[i];
    }
    
    // manin recursion loop
    // increment current position and send data to next recursion
    while (current[pos] <= maximum[pos]) {
        
        // check high mass and stored items limits
        if ( (mass > hiMass) || (p_result->len >= limit) ) {
            break;
        }
        
        // do next recursion
        formula_generator( p_result, elcount, current, maximum, masses, loMass, hiMass, limit, pos+1);
        current[pos]++;
        mass += masses[pos];
    }
    
    // free buffer
    free(current);
}

m_arrayi *formula_composition( int elcount, int minimum[], int maximum[], double masses[], double loMass, double hiMass, int limit )
{
    m_arrayi *p_buff, *p_result;
    int i;
    
    // init buffer
    if ( (p_buff = (m_arrayi*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_buff->data = (int*) malloc( limit*elcount*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_buff->len = 0;
    p_buff->dim = 2;
    p_buff->cell = elcount;
    
    // generate compositions
    formula_generator( p_buff, elcount, minimum, maximum, masses, loMass, hiMass, limit, 0);
    
    // check compositions
    if (p_buff->len == 0) {
        return NULL;
    }
    
    // init results
    if ( (p_result = (m_arrayi*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    if ( (p_result->data = (int*) malloc( p_buff->len*elcount*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    p_result->len = p_buff->len;
    p_result->dim = 2;
    p_result->cell = elcount;
    
    // copy compositions
    for ( i = 0; i < p_buff->len*elcount; ++i ) {
        p_result->data[i] = p_buff->data[i];
    }
    
    // free buffer
    free(p_buff->data);
    free(p_buff);
    
    return p_result;
}


// HELPERS
// --------------------------------------------------------------------------

m_arrayd *array_py2md( PyArrayObject *p_inarr )
{
    m_arrayd *p_outarr;
    int len, dim, cell;
    
    // get array dimensions
    len = (int) PyArray_DIM(p_inarr, 0);
    dim = cell = (int) PyArray_NDIM(p_inarr);
    if ( dim == 2 ) cell = (int) PyArray_DIM(p_inarr, 1);
    
    // make m_arrayd
    if ( (p_outarr = (m_arrayd*) malloc( sizeof(m_arrayd)) ) == NULL ) {
        return NULL;
    }
    p_outarr->data = (double *) p_inarr->data;
    p_outarr->len = len;
    p_outarr->dim = dim;
    p_outarr->cell = cell;
    
    return p_outarr;
}

PyArrayObject *array_md2py( m_arrayd *p_inarr )
{
    PyArrayObject *p_outarr;
    npy_intp dim[2];
    double *p_outarr_data;
    int nd;
    int i;
    
    // get array size
    nd = p_inarr->dim;
    dim[0] = (npy_intp) p_inarr->len;
    dim[1] = (npy_intp) p_inarr->cell;
    
    // make python array
    p_outarr = (PyArrayObject *) PyArray_SimpleNew(nd, dim, PyArray_DOUBLE);
    if ( p_outarr == NULL ) {
        return NULL;
    }
    
    // copy data
    p_outarr_data = (double *) p_outarr->data;
    for ( i = 0; i < (p_inarr->len*p_inarr->cell); i++ ) {
      p_outarr_data[i] = p_inarr->data[i];
    }
    
    return p_outarr;
}

PyObject *list_mi2py( m_arrayi *p_inarr )
{
    PyObject *p_outlist, *p_inner, *p_item;
    int i, j;
    
    // make empty list
    if ( p_inarr == NULL ) {
        p_outlist = PyList_New(0);
    }
    
    // make 1D list
    else if ( p_inarr->dim == 1 ) {
        p_outlist = PyList_New( p_inarr->len );
        for ( i = 0; i < p_inarr->len; ++i ) {
            p_item = PyInt_FromLong( p_inarr->data[i] );
            PyList_SetItem( p_outlist, i, p_item );
        }
    }
    
    // make 2D list
    else if ( p_inarr->dim == 2) {
        p_outlist = PyList_New(0);
        for ( i = 0; i < p_inarr->len; ++i ) {
            p_inner = PyList_New( p_inarr->cell );
            for ( j = 0; j < p_inarr->cell; ++j ) {
                p_item = PyInt_FromLong( p_inarr->data[i*p_inarr->cell+j] );
                PyList_SetItem( p_inner, j,  p_item);
            }
            PyList_Append(p_outlist, p_inner);
        }
    }
    
    else {
        p_outlist = PyList_New(0);
    }
    
    return p_outlist;
}


// PYTHON WRAPERS
// --------------------------------------------------------------------------

static PyObject *_wrap_signal_interpolate_x( PyObject *self, PyObject *args )
{
    double x1, x2, y1, y2, y;
    double result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "ddddd", &x1, &y1, &x2, &y2, &y) ) {
        return NULL;
    }
    
    // interpolate point
    result = signal_interpolate_x( x1, y1, x2, y2, y );
    
    return Py_BuildValue("d", result);
}

static PyObject *_wrap_signal_interpolate_y( PyObject *self, PyObject *args )
{
    double x1, x2, y1, y2, x;
    double result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "ddddd", &x1, &y1, &x2, &y2, &x) ) {
        return NULL;
    }
    
    // interpolate point
    result = signal_interpolate_y( x1, y1, x2, y2, x );
    
    return Py_BuildValue("d", result);
}

// ----------

static PyObject *_wrap_signal_locate_x( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal;
    m_arrayd *p_msignal;
    double x;
    int result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Od", &p_signal, &x) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get index
    result = signal_locate_x( p_msignal, x );
    
    // free memory
    free(p_msignal);
    
    return Py_BuildValue("i", result);
}

static PyObject *_wrap_signal_locate_max_y( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal;
    m_arrayd *p_msignal;
    int result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "O", &p_signal) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get index
    result = signal_locate_max_y( p_msignal );
    
    // free memory
    free(p_msignal);
    
    return Py_BuildValue("i", result);
}

static PyObject *_wrap_signal_box( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal;
    m_arrayd *p_msignal;
    m_box result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "O", &p_signal) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get bounding box
    result = signal_box( p_msignal );
    
    // free memory
    free(p_msignal);
    
    return Py_BuildValue("dddd", result.minX, result.minY, result.maxX, result.maxY);
}

// ----------

static PyObject *_wrap_signal_intensity( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal;
    m_arrayd *p_msignal;
    double x, result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Od", &p_signal, &x) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get intensity
    result = signal_intensity( p_msignal, x );
    
    // free memory
    free(p_msignal);
    
    return Py_BuildValue("d", result);
}

static PyObject *_wrap_signal_centroid( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal;
    m_arrayd *p_msignal;
    double x, height, result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Odd", &p_signal, &x, &height) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get centroid
    result = signal_centroid( p_msignal, x, height );
    
    // free memory
    free(p_msignal);
    
    return Py_BuildValue("d", result);
}

static PyObject *_wrap_signal_width( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal;
    m_arrayd *p_msignal;
    double x, height, result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Odd", &p_signal, &x, &height) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get width
    result = signal_width( p_msignal, x, height );
    
    // free memory
    free(p_msignal);
    
    return Py_BuildValue("d", result);
}

static PyObject *_wrap_signal_area( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal;
    m_arrayd *p_msignal;
    double result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "O", &p_signal) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get area
    result = signal_area( p_msignal );
    
    // free memory
    free(p_msignal);
    
    return Py_BuildValue("d", result);
}

static PyObject *_wrap_signal_noise( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal;
    m_arrayd *p_msignal;
    m_noise result;
    
    // get params
    if ( !PyArg_ParseTuple(args, "O", &p_signal) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get noise
    result = signal_noise( p_msignal );
    
    // free memory
    free(p_msignal);
    
    return Py_BuildValue("dd", result.level, result.width);
}

static PyObject *_wrap_signal_local_maxima( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    
    // get params
    if ( !PyArg_ParseTuple(args, "O", &p_signal) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // get local maxima
    p_mresults = signal_local_maxima( p_msignal );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

// ----------

static PyObject *_wrap_signal_crop( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    double minX, maxX;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Odd", &p_signal, &minX, &maxX) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // crop signal
    p_mresults = signal_crop( p_msignal, minX, maxX );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_offset( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    double x, y;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Odd", &p_signal, &x, &y) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // offset signal
    p_mresults = signal_offset( p_msignal, x, y );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_multiply( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    double x, y;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Odd", &p_signal, &x, &y) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // multiply signal
    p_mresults = signal_multiply( p_msignal, x, y );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_normalize( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    
    // get params
    if ( !PyArg_ParseTuple(args, "O", &p_signal) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // normalize signal
    p_mresults = signal_normalize( p_msignal );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_smooth_ma( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    int window, cycles;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Oii", &p_signal, &window, &cycles) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // smooth signal
    p_mresults = signal_smooth_ma( p_msignal, window, cycles );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_smooth_ga( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    int window, cycles;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Oii", &p_signal, &window, &cycles) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // smooth signal
    p_mresults = signal_smooth_ga( p_msignal, window, cycles );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_combine( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signalA, *p_signalB, *p_results;
    m_arrayd *p_msignalA, *p_msignalB, *p_mresults;
    
    // get params
    if ( !PyArg_ParseTuple(args, "OO", &p_signalA, &p_signalB) ) {
        return NULL;
    }
    
    // convert signals to m_arrayd
    p_msignalA = array_py2md(p_signalA);
    p_msignalB = array_py2md(p_signalB);
    
    // combine signals
    p_mresults = signal_combine( p_msignalA, p_msignalB );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignalA);
    free(p_msignalB);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_overlay( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signalA, *p_signalB, *p_results;
    m_arrayd *p_msignalA, *p_msignalB, *p_mresults;
    
    // get params
    if ( !PyArg_ParseTuple(args, "OO", &p_signalA, &p_signalB) ) {
        return NULL;
    }
    
    // convert signals to m_arrayd
    p_msignalA = array_py2md(p_signalA);
    p_msignalB = array_py2md(p_signalB);
    
    // overlay signals
    p_mresults = signal_overlay( p_msignalA, p_msignalB );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignalA);
    free(p_msignalB);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_subtract( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signalA, *p_signalB, *p_results;
    m_arrayd *p_msignalA, *p_msignalB, *p_mresults;
    
    // get params
    if ( !PyArg_ParseTuple(args, "OO", &p_signalA, &p_signalB) ) {
        return NULL;
    }
    
    // convert signals to m_arrayd
    p_msignalA = array_py2md(p_signalA);
    p_msignalB = array_py2md(p_signalB);
    
    // subtract signals
    p_mresults = signal_subtract( p_msignalA, p_msignalB );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignalA);
    free(p_msignalB);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_subbase( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_baseline, *p_results;
    m_arrayd *p_msignal, *p_mbaseline, *p_mresults;
    
    // get params
    if ( !PyArg_ParseTuple(args, "OO", &p_signal, &p_baseline) ) {
        return NULL;
    }
    
    // convert signals to m_arrayd
    p_msignal = array_py2md(p_signal);
    p_mbaseline = array_py2md(p_baseline);
    
    // subtract baseline
    p_mresults = signal_subbase( p_msignal, p_mbaseline );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mbaseline);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

// ----------

static PyObject *_wrap_signal_rescale( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    double scaleX, scaleY, shiftX, shiftY;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Odddd", &p_signal, &scaleX, &scaleY, &shiftX, &shiftY) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // rescale signal
    p_mresults = signal_rescale( p_msignal, scaleX, scaleY, shiftX, shiftY );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_filter( PyObject *self, PyObject *args )
{
    PyArrayObject *p_signal, *p_results;
    m_arrayd *p_msignal, *p_mresults;
    double resol;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Od", &p_signal, &resol) ) {
        return NULL;
    }
    
    // convert signal to m_arrayd
    p_msignal = array_py2md(p_signal);
    
    // filter signal
    p_mresults = signal_filter( p_msignal, resol );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_msignal);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

// ----------

static PyObject *_wrap_signal_gaussian( PyObject *self, PyObject *args )
{
    PyArrayObject *p_results;
    m_arrayd *p_mresults;
    double x, minY, maxY, fwhm;
    int points;
    
    // get params
    if ( !PyArg_ParseTuple(args, "ddddi", &x, &minY, &maxY, &fwhm, &points) ) {
        return NULL;
    }
    
    // make gaussian peak
    p_mresults = signal_gaussian( x, minY, maxY, fwhm, points );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_lorentzian( PyObject *self, PyObject *args )
{
    PyArrayObject *p_results;
    m_arrayd *p_mresults;
    double x, minY, maxY, fwhm;
    int points;
    
    // get params
    if ( !PyArg_ParseTuple(args, "ddddi", &x, &minY, &maxY, &fwhm, &points) ) {
        return NULL;
    }
    
    // make gaussian peak
    p_mresults = signal_lorentzian( x, minY, maxY, fwhm, points );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_gausslorentzian( PyObject *self, PyObject *args )
{
    PyArrayObject *p_results;
    m_arrayd *p_mresults;
    double x, minY, maxY, fwhm;
    int points;
    
    // get params
    if ( !PyArg_ParseTuple(args, "ddddi", &x, &minY, &maxY, &fwhm, &points) ) {
        return NULL;
    }
    
    // make gauss-lorentzian peak
    p_mresults = signal_gausslorentzian( x, minY, maxY, fwhm, points );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_profile( PyObject *self, PyObject *args )
{
    PyArrayObject *p_peaks, *p_results;
    m_arrayd *p_mpeaks, *p_mresults;
    double noise;
    int shape;
    int points;
    
    // get params
    if ( !PyArg_ParseTuple(args, "Oidi", &p_peaks, &points, &noise, &shape) ) {
        return NULL;
    }
    
    // convert peaks to m_arrayd
    p_mpeaks = array_py2md(p_peaks);
    
    // make profile
    p_mresults = signal_profile( p_mpeaks, points, noise, shape );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_mpeaks);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

static PyObject *_wrap_signal_profile_to_raster( PyObject *self, PyObject *args )
{
    PyArrayObject *p_peaks, *p_raster, *p_results;
    m_arrayd *p_mpeaks, *p_mraster, *p_mresults;
    double noise;
    int shape;
    
    // get params
    if ( !PyArg_ParseTuple(args, "OOdi", &p_peaks, &p_raster, &noise, &shape) ) {
        return NULL;
    }
    
    // convert peaks and raster to m_arrayd
    p_mpeaks = array_py2md(p_peaks);
    p_mraster = array_py2md(p_raster);
    
    // make profile
    p_mresults = signal_profile_to_raster( p_mpeaks, p_mraster, noise, shape );
    
    // make numpy array
    p_results = array_md2py( p_mresults );
    
    // free memory
    free(p_mpeaks);
    free(p_mraster);
    free(p_mresults->data);
    free(p_mresults);
    
    return PyArray_Return(p_results);
}

// ----------

static PyObject *_wrap_formula_composition( PyObject *self, PyObject *args )
{
    PyObject *p_minimum, *p_maximum, *p_masses;
    PyObject *p_results;
    m_arrayi *p_mresults;
    int *p_cminimum, *p_cmaximum;
    double *p_cmasses;
    double loMass, hiMass;
    int limit, elcount;
    int i;
    
    // get params
    if ( !PyArg_ParseTuple(args, "OOOddi", &p_minimum, &p_maximum, &p_masses, &loMass, &hiMass, &limit) ) {
        return NULL;
    }
    
    // get elements count
    elcount = (int) PyTuple_Size(p_minimum);
    
    // init input arrays
    if ( (p_cminimum = (int*) malloc( elcount*sizeof(int)) ) == NULL ) {
        return NULL;
    }
    if ( (p_cmaximum = (int*) malloc( elcount*sizeof(int)) ) == NULL ) {
        return NULL;
    }
    if ( (p_cmasses = (double*) malloc( elcount*sizeof(double)) ) == NULL ) {
        return NULL;
    }
    for ( i = 0; i < elcount; ++i) {
        p_cminimum[i] = (int) PyLong_AsLong(PyTuple_GetItem(p_minimum, i));
        p_cmaximum[i] = (int) PyLong_AsLong(PyTuple_GetItem(p_maximum, i));
        p_cmasses[i] = (double) PyFloat_AsDouble(PyTuple_GetItem(p_masses, i));
    }
    
    // generate compositions
    p_mresults = formula_composition( elcount, p_cminimum, p_cmaximum, p_cmasses, loMass, hiMass, limit );
    
    // make python list
    p_results = list_mi2py( p_mresults );
    
    // free memory
    free(p_cminimum);
    free(p_cmaximum);
    free(p_cmasses);
    
    if ( p_mresults != NULL ) {
        free(p_mresults->data);
        free(p_mresults);
    }
    
    return p_results;
}


// PYTHON METHODS
// --------------------------------------------------------------------------

static PyMethodDef calculations_methods[] = {
   
   {"signal_interpolate_x", _wrap_signal_interpolate_x, METH_VARARGS, "signal_interpolate_x( double, double, double, double, double )"},
   {"signal_interpolate_y", _wrap_signal_interpolate_y, METH_VARARGS, "signal_interpolate_y( double, double, double, double, double )"},
   
   {"signal_locate_x", _wrap_signal_locate_x, METH_VARARGS, "signal_locate_x( PyArray, double )"},
   {"signal_locate_max_y", _wrap_signal_locate_max_y, METH_VARARGS, "signal_locate_max_y( PyArray )"},
   {"signal_box", _wrap_signal_box, METH_VARARGS, "signal_box( PyArray )"},
   
   {"signal_intensity", _wrap_signal_intensity, METH_VARARGS, "signal_intensity( PyArray, double )"},
   {"signal_centroid", _wrap_signal_centroid, METH_VARARGS, "signal_centroid( PyArray, double, double )"},
   {"signal_width", _wrap_signal_width, METH_VARARGS, "signal_width( PyArray, double, double )"},
   {"signal_area", _wrap_signal_area, METH_VARARGS, "signal_area( PyArray )"},
   {"signal_noise", _wrap_signal_noise, METH_VARARGS, "signal_noise( PyArray )"},
   {"signal_local_maxima", _wrap_signal_local_maxima, METH_VARARGS, "signal_local_maxima( PyArray )"},
   
   {"signal_crop", _wrap_signal_crop, METH_VARARGS, "signal_crop( PyArray, double, double )"},
   {"signal_offset", _wrap_signal_offset, METH_VARARGS, "signal_offset( PyArray, double, double )"},
   {"signal_multiply", _wrap_signal_multiply, METH_VARARGS, "signal_multiply( PyArray, double, double )"},
   {"signal_normalize", _wrap_signal_normalize, METH_VARARGS, "signal_normalize( PyArray )"},
   {"signal_smooth_ma", _wrap_signal_smooth_ma, METH_VARARGS, "signal_smooth_ma( PyArray, int, int )"},
   {"signal_smooth_ga", _wrap_signal_smooth_ga, METH_VARARGS, "signal_smooth_ga( PyArray, int, int )"},
   {"signal_combine", _wrap_signal_combine, METH_VARARGS, "signal_combine( PyArray, PyArray )"},
   {"signal_overlay", _wrap_signal_overlay, METH_VARARGS, "signal_overlay( PyArray, PyArray )"},
   {"signal_subtract", _wrap_signal_subtract, METH_VARARGS, "signal_subtract( PyArray, PyArray )"},
   {"signal_subbase", _wrap_signal_subbase, METH_VARARGS, "signal_subbase( PyArray, PyArray )"},
   
   {"signal_rescale", _wrap_signal_rescale, METH_VARARGS, "signal_rescale( PyArray, double, double, double, double )"},
   {"signal_filter", _wrap_signal_filter, METH_VARARGS, "signal_filter( PyArray, double )"},
   
   {"signal_gaussian", _wrap_signal_gaussian, METH_VARARGS, "signal_gaussian( double, double, double, double, int, double )"},
   {"signal_lorentzian", _wrap_signal_lorentzian, METH_VARARGS, "signal_lorentzian( double, double, double, double, int, double )"},
   {"signal_gausslorentzian", _wrap_signal_gausslorentzian, METH_VARARGS, "signal_gausslorentzian( double, double, double, double, int, double )"},
   {"signal_profile", _wrap_signal_profile, METH_VARARGS, "signal_profile( PyArray, int, double, int )"},
   {"signal_profile_to_raster", _wrap_signal_profile_to_raster, METH_VARARGS, "signal_profile_to_raster( PyArray, PyArray, double, int )"},
   
   {"formula_composition", _wrap_formula_composition, METH_VARARGS, "formula_composition( PyTupleObject, PyTupleObject, PyTupleObject, double, double, int )"},
   
   {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initcalculations(void) {
    Py_InitModule3("calculations", calculations_methods,"");
    import_array();
}