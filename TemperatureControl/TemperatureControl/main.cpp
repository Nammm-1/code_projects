#include <iostream>
using namespace std;
int main(){
        int list1[5]={1,3,5,7,9}; //initialize list1 array
        int list2[5];
        int i;
        
        for(i=0;i<5;i++){
            list2[i]=list1[i]+1; //assign values to list2
      
            cout<<list2[i]<<"\t";
        }
    
    return 0;
}
