int add ( int a , int b ) {
    return a + b ;
}
int test ( int a , int b ) {
    int c = a + b ;
    c = 4 + 5 + 3 + 9 + 2 + a ;
    return c ;
}
int main ( ) {
    int a = 5 ;
    int b = 10 ;
    int c ;
    c = add ( a , b ) ;
    int d = test ( a , c ) ;
    return 0 ;
}
