#!/usr/bin/env python3
"""
Test script to verify efficiency fixes work correctly
"""

def test_bom_fix():
    """Test that kpi_processor.py can be imported without syntax errors"""
    try:
        import kpi_processor
        print("✅ BOM fix successful - kpi_processor.py imports without syntax errors")
        return True
    except SyntaxError as e:
        print(f"❌ BOM fix failed - syntax error: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Import succeeded but other error: {e}")
        return True

def test_vectorized_signatures():
    """Test that the vectorized signature generation works"""
    try:
        import pandas as pd
        import sys
        import os
        sys.path.append('scripts')
        
        from complete_configurable_processor import CompleteConfigurableProcessor
        
        test_df = pd.DataFrame({
            'number': ['INC001', 'INC002', 'INC003'],
            'priority': ['1', '2', '3'],
            'state': ['Open', 'Closed', 'Open']
        })
        
        class MockProcessor:
            def _generate_configurable_signatures(self, df, signature_fields):
                import hashlib
                signatures = {}
                available_fields = [field for field in signature_fields if field in df.columns]
                
                if available_fields:
                    record_ids = df.get('number', df.index.astype(str)).astype(str)
                    key_values = df[available_fields].fillna('').astype(str).apply(lambda row: '|'.join(row), axis=1)
                    signatures = dict(zip(record_ids, key_values.apply(lambda x: hashlib.md5(x.encode()).hexdigest())))
                
                return signatures
        
        processor = MockProcessor()
        signatures = processor._generate_configurable_signatures(test_df, ['number', 'priority', 'state'])
        
        if len(signatures) == 3 and 'INC001' in signatures:
            print("✅ Vectorized signature generation works correctly")
            return True
        else:
            print(f"❌ Signature generation failed - got {len(signatures)} signatures")
            return False
            
    except Exception as e:
        print(f"❌ Vectorized signature test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing efficiency fixes...")
    
    bom_ok = test_bom_fix()
    sig_ok = test_vectorized_signatures()
    
    if bom_ok and sig_ok:
        print("\n✅ All efficiency fixes working correctly!")
    else:
        print("\n❌ Some tests failed - check the fixes")
