#ifndef _SPARSEPOLYKERNEL_H___
#define _SPARSEPOLYKERNEL_H___

#include "lib/common.h"
#include "kernel/SparseRealKernel.h"
#include "features/SparseRealFeatures.h"

class CSparsePolyKernel: public CSparseRealKernel
{
 public:
  CSparsePolyKernel(long size, int degree, bool inhomogene);
  ~CSparsePolyKernel();
  
  virtual void cleanup();

  /// load and save kernel init_data
  virtual bool load_init(FILE* src);
  virtual bool save_init(FILE* dest);

  /** return feature type the kernel can deal with
  */
  inline virtual EFeatureType get_feature_type() { return F_REAL; }

  // return what type of kernel we are Linear,Polynomial, Gaussian,...
  virtual EKernelType get_kernel_type() { return K_POLY; }

  // return the name of a kernel
  virtual const char* get_name() { return "SparsePoly" ; } ;

 protected:
  /// compute kernel function for features a and b
  /// idx_{a,b} denote the index of the feature vectors
  /// in the corresponding feature object
  virtual REAL compute(long idx_a, long idx_b);
  /*    compute_kernel*/
  
 protected:
  int degree;
  bool inhomogene ;
};
#endif
