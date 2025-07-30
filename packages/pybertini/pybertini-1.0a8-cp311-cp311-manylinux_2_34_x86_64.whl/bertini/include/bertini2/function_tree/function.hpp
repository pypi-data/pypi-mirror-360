//This file is part of Bertini 2.
//
//bertini2/function_tree/roots/function.hpp is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or
//(at your option) any later version.
//
//bertini2/function_tree/roots/function.hpp is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with bertini2/function_tree/roots/function.hpp.  If not, see <http://www.gnu.org/licenses/>.
//
// Copyright(C) 2015 - 2021 by Bertini2 Development Team
//
// See <http://www.gnu.org/licenses/> for a copy of the license, 
// as well as COPYING.  Bertini2 is provided with permitted 
// additional terms in the b2/licenses/ directory.

// individual authors of this file include:
//  James Collins
//  West Texas A&M University
//  Spring, Summer 2015
//
// silviana amethyst, university of wisconsin-eau claire
//
//  silviana amethyst
//  UWEC
//  Spring 2018
//
//  Created by Collins, James B. on 4/30/15.
//
//
// bertini2/function_tree/roots/function.hpp:  Declares the class Function.

/**
\file bertini2/function_tree/roots/function.hpp

\brief Provides the Function Node type, a NamedSymbol.

*/


#ifndef BERTINI_FUNCTION_NODE_HPP
#define BERTINI_FUNCTION_NODE_HPP


#include "bertini2/function_tree/symbols/symbol.hpp"



namespace bertini {
namespace node{
	


	class Handle : public virtual NamedSymbol
	{
		BERTINI_DEFAULT_VISITABLE()


	public:

		/**
		 overridden function for piping the tree to an output stream.
		 */
		void print(std::ostream & target) const override;


		Handle(std::string const& new_name);
		
		
		/**
		 Constructor defines entry node at construct time.
		 */
		Handle(const std::shared_ptr<Node> & entry, std::string const& name = "unnamed_function");


	protected:

		Handle() = default;

	public:
		/**
		 Add a child onto the container for this operator
		 */
		void SetRoot(std::shared_ptr<Node> const& entry);


		/**
		 throws a runtime error if the root node is nullptr
		 */
		void EnsureNotEmpty() const;


		/**
		 The function which flips the fresh eval bit back to fresh.
		 */
		void Reset() const override;



		/**
		 Get the pointer to the entry node for this function.
		 */
		const std::shared_ptr<Node>& EntryNode() const;


		/** 
		 Calls Differentiate on the entry node and returns differentiated entry node.
		 */
		std::shared_ptr<Node> Differentiate(std::shared_ptr<Variable> const& v = nullptr) const override;

		/**
		Compute the degree of a node.  For functions, the degree is the degree of the entry node.
		*/
		int Degree(std::shared_ptr<Variable> const& v = nullptr) const override;


		int Degree(VariableGroup const& vars) const override;



		/**
		 Compute the multidegree with respect to a variable group.  This is for homogenization, and testing for homogeneity.  
		*/
		std::vector<int> MultiDegree(VariableGroup const& vars) const override;


		void Homogenize(VariableGroup const& vars, std::shared_ptr<Variable> const& homvar) override;

		bool IsHomogeneous(std::shared_ptr<Variable> const& v = nullptr) const override;

		/**
		Check for homogeneity, with respect to a variable group.
		*/
		bool IsHomogeneous(VariableGroup const& vars) const override;


		/**
		 Change the precision of this variable-precision tree node.
		 
		 \param prec the number of digits to change precision to.
		 */
		void precision(unsigned int prec) const override;

		

	protected:
		
		/**
		 Calls FreshEval on the entry node to the tree.
		 */
		dbl FreshEval_d(std::shared_ptr<Variable> const& diff_variable) const override;
		
		/**
		 Calls FreshEval in place on the entry node to the tree.
		 */
		void FreshEval_d(dbl& evaluation_value, std::shared_ptr<Variable> const& diff_variable) const override;

		
		/**
		 Calls FreshEval on the entry node to the tree.
		 */
		mpfr_complex FreshEval_mp(std::shared_ptr<Variable> const& diff_variable) const override;
		
		/**
		 Calls FreshEval in place on the entry node to the tree.
		 */
		void FreshEval_mp(mpfr_complex& evaluation_value, std::shared_ptr<Variable> const& diff_variable) const override;


		std::shared_ptr<Node> entry_node_ = nullptr;

	private:



		friend class boost::serialization::access;

		template <typename Archive>
		void serialize(Archive& ar, const unsigned version) {
			ar & boost::serialization::base_object<NamedSymbol>(*this);
			ar & entry_node_;
		}

	}; // class Function




}} // namespaces














namespace bertini {
namespace node{

	/**
	\brief Formal entry point into an expression tree.

	This class defines a function.  It stores the entry node for a particular functions tree.
	 */
	class Function : public virtual Handle, public virtual EnableSharedFromThisVirtual<Function>
	{
	public:
		BERTINI_DEFAULT_VISITABLE()
		
		template<typename... Ts> 
		static 
		std::shared_ptr<Function> Make(Ts&& ...ts){ 
			return std::shared_ptr<Function>( new Function(ts...) );
		}

		template<typename... Ts> 
		static 
		std::shared_ptr<Function> MakeInPlace(Function* ptr, Ts&& ...ts){ 
			return std::shared_ptr<Function>( new(ptr) Function(ts...) );
		}

	private:

		Function(std::string const& new_name);
		
		
		/**
		 Constructor defines entry node at construct time.
		 */
		Function(const std::shared_ptr<Node> & entry, std::string const& name = "unnamed_function");
		
	public:

		
		
		virtual ~Function() = default;
		
		
		
	protected:
		
		
		Function() = default;


	private:
		friend class boost::serialization::access;
		// template<class Archive> friend void boost::serialization::load_construct_data(Archive & ar, Function * t, const unsigned int file_version);
		// template<class Archive> friend void boost::serialization::save_construct_data(Archive & ar, const Function * t, const unsigned int file_version);

		template <typename Archive>
		void serialize(Archive& ar, const unsigned version) {
			ar & boost::serialization::base_object<Handle>(*this);
		}
	};
	
} // re: namespace node
} // re: namespace bertini



#endif
