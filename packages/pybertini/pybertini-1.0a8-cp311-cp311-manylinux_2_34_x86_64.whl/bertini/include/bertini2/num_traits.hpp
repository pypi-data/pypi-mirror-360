//This file is part of Bertini 2.
//
//num_traits.hpp is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or
//(at your option) any later version.
//
//num_traits.hpp is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with num_traits.hpp.  If not, see <http://www.gnu.org/licenses/>.
//
// Copyright(C) 2015 - 2021 by Bertini2 Development Team
//
// See <http://www.gnu.org/licenses/> for a copy of the license, 
// as well as COPYING.  Bertini2 is provided with permitted 
// additional terms in the b2/licenses/ directory.

// individual authors of this file include:
// silviana amethyst, university of wisconsin eau claire

/**
\file num_traits.hpp 

\brief Provides an Eigen-like NumTraits struct for querying traits of a number type.  

The bertini::NumTraits struct provides NumDigits and NumFuzzyDigits functions.
*/

#ifndef BERTINI_NUM_TRAITS_HPP
#define BERTINI_NUM_TRAITS_HPP

#include <random>
#include <complex>
#include <cmath>
#include "bertini2/mpfr_complex.hpp"
#include "bertini2/random.hpp"


namespace bertini
{
	template<typename T>
	T RandomUnit();

	template<typename T>
	struct NumTraits
	{};



	template <> struct NumTraits<double> 
	{
		inline static unsigned NumDigits()
		{
			return 16;
		}

		inline static unsigned NumFuzzyDigits()
		{
			return 14;
		}

		inline
		static unsigned TolToDigits(double tol)
		{
			return ceil(-log10(tol));
		}

		inline static 
		double FromString(std::string const& s)
		{
			return boost::lexical_cast<double>(s);
		}

		inline static
		double FromRational(mpq_rational const& n, unsigned /* precision */)
		{
			return double(n);
		}

		using Real = double;
		using Complex = dbl_complex;
	};


	template <> struct NumTraits<dbl_complex > 
	{
		inline static unsigned NumDigits()
		{
			return 16;
		}

		inline static unsigned NumFuzzyDigits()
		{
			return 14;
		}

		inline static 
		dbl_complex FromString(std::string const& s)
		{
			return boost::lexical_cast<dbl_complex>(s);
		}

		inline static 
		dbl_complex FromString(std::string const& s, std::string const& t)
		{
			return dbl_complex(boost::lexical_cast<double>(s),boost::lexical_cast<double>(t));
		}

		inline static
		dbl_complex FromRational(mpq_rational const& n, unsigned /* precision */)
		{
			return dbl_complex(static_cast<double>(n),0);
		}

		using Real = double;
		using Complex = dbl_complex;
	};


	inline
	unsigned PrecisionIncrement()
	{
		return 10;
	}

	inline
	unsigned DoublePrecision()
	{
		return 16;
	}

	inline
	unsigned LowestMultiplePrecision()
	{
		return 20;
	}
		
	inline
	unsigned MaxPrecisionAllowed()
	{
		return 1000;
	}
	
	/**
	\brief Get the precision of a number.

	For doubles, this is trivially 16.
	*/
	inline
	unsigned Precision(double)
	{
		return DoublePrecision();
	}

	/**
	For complex doubles, throw if the requested precision is not DoublePrecision.
	*/
	inline
	void Precision(double, unsigned prec)
	{
		if (prec!=DoublePrecision())
		{
			std::stringstream err_msg;
			err_msg << "trying to change precision of a double to " << prec;
			throw std::runtime_error(err_msg.str());
		}
	}

	/**
	\brief Get the precision of a number.

	For complex doubles, this is trivially 16.
	*/
	inline
	unsigned Precision(dbl_complex)
	{
		return DoublePrecision();
	}

	/**
	For complex doubles, throw if the requested precision is not DoublePrecision.
	*/
	inline
	void Precision(dbl_complex, unsigned prec)
	{
		if (prec!=DoublePrecision())
		{
			std::stringstream err_msg;
			err_msg << "trying to change precision of a double to " << prec;
			throw std::runtime_error(err_msg.str());
		}
	}

	inline
	dbl_complex rand_complex()
	{
		using std::abs;
		using std::sqrt;
		static std::default_random_engine generator;
		static std::uniform_real_distribution<double> distribution(-1.0,1.0);
		dbl_complex returnme(distribution(generator), distribution(generator));
		return returnme / sqrt( abs(returnme));
	}

	template <> inline
	dbl_complex RandomUnit<dbl_complex >()
	{
		static std::default_random_engine generator;
		static std::uniform_real_distribution<double> distribution(-1.0,1.0);
		dbl_complex returnme(distribution(generator), distribution(generator));
		return returnme / abs(returnme);
	}

	template <> 
	inline 
	mpfr_complex RandomUnit<mpfr_complex>()
	{
		return multiprecision::RandomUnit();
	}
}// re: namespace bertini












namespace bertini {

	
	
	template <> struct NumTraits<mpfr_float> 
	{
		inline static unsigned NumDigits()
		{
			return DefaultPrecision();
		}

		inline static unsigned NumFuzzyDigits()
		{
			return DefaultPrecision()-3;
		}

		inline
		static unsigned TolToDigits(mpfr_float tol)
		{
			mpfr_float b = ceil(-log10(tol));
			return b.convert_to<unsigned int>();
		}

		inline static 
		mpfr_float FromString(std::string const& s)
		{
			return mpfr_float(s);
		}

		inline static
		mpfr_float FromRational(mpq_rational const& n, unsigned precision)
		{
			return mpfr_float(n,precision);
		}

		using Real = mpfr_float;
		using Complex = mpfr_complex;
	};	



	template <> struct NumTraits<mpfr_complex> 
	{
		inline static unsigned NumDigits()
		{
			return DefaultPrecision();
		}

		inline static 
		mpfr_complex FromString(std::string const& s)
		{
			return mpfr_complex(s);
		}

		inline static 
		mpfr_complex FromString(std::string const& s, std::string const& t)
		{
			return mpfr_complex(s,t);
		}

		inline static
		mpfr_complex FromRational(mpq_rational const& n, unsigned precision)
		{
			return mpfr_complex(n,0,precision);
		}

		using Real = mpfr_float;
		using Complex = mpfr_complex;
	};

	template <> struct NumTraits<mpq_rational> 
	{
		inline static 
		mpq_rational FromString(std::string const& s)
		{
			return mpq_rational(s);
		}
	};	

}

#endif


