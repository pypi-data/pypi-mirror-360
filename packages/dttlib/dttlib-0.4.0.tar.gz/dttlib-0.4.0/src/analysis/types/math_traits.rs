use pipelines::complex::c128;
use pipelines::PipeData;

pub (crate) trait Sqrt {
    type Output: PipeData;
    
    fn square_root(&self) -> Self::Output;
}

impl Sqrt for f64 {
    type Output = f64;

    fn square_root(&self) -> Self::Output {
        (*self).sqrt()
    }
}

impl Sqrt for c128 {
    type Output = c128;

    fn square_root(&self) -> Self::Output {
        (*self).sqrt()
    }
}