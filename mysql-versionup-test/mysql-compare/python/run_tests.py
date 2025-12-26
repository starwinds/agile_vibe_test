

import os
import subprocess
import json
import time
from datetime import datetime

# 테스트 스크립트가 위치한 디렉토리
TESTS_DIR = 'tests'
# 결과 파일을 저장할 디렉토리
RESULTS_DIR = 'test_results'

def find_test_scripts():
    """'tests' 디렉토리에서 'test_*.py'로 시작하는 모든 테스트 스크립트 파일을 찾습니다."""
    scripts = []
    if not os.path.exists(TESTS_DIR):
        print(f"오류: '{TESTS_DIR}' 디렉토리를 찾을 수 없습니다.")
        return scripts

    for filename in sorted(os.listdir(TESTS_DIR)):
        if filename.startswith('test_') and filename.endswith('.py'):
            scripts.append(os.path.join(TESTS_DIR, filename))
    return scripts

def run_single_test(script_path):
    """단일 테스트 스크립트를 실행하고 결과를 반환합니다."""
    print(f"▶️  실행 중: {script_path}")
    start_time = time.time()
    
    try:
        # 스크립트 경로를 모듈 경로로 변환 (e.g., 'tests/test_auth.py' -> 'tests.test_auth')
        module_path = os.path.splitext(script_path)[0].replace(os.sep, '.')

        # Python 스크립트를 모듈로 실행하여 경로 문제를 해결합니다.
        process = subprocess.run(
            ['python3', '-m', module_path],
            capture_output=True,
            text=True,
            timeout=300  # 5분 타임아웃
        )
        status = 'success' if process.returncode == 0 else 'failure'
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        
        if status == 'failure':
            print(f"❗ 실패: {script_path} (종료 코드: {process.returncode})")
        else:
            print(f"✅ 성공: {script_path}")

    except subprocess.TimeoutExpired:
        status = 'timeout'
        stdout = ''
        stderr = '스크립트 실행 시간이 5분을 초과했습니다.'
        print(f"⌛ 타임아웃: {script_path}")
    except Exception as e:
        status = 'error'
        stdout = ''
        stderr = f"스크립트 실행 중 예외 발생: {str(e)}"
        print(f"❌ 오류: {script_path}")

    end_time = time.time()
    duration = round(end_time - start_time, 4)

    return {
        'script': script_path,
        'status': status,
        'duration_seconds': duration,
        'stdout': stdout,
        'stderr': stderr,
    }

def main():
    """테스트 실행을 총괄하고 결과를 JSON 파일로 저장합니다."""
    print("MySQL 호환성 테스트를 시작합니다...")
    test_scripts = find_test_scripts()

    if not test_scripts:
        print("실행할 테스트 스크립트가 없습니다.")
        return

    all_results = []
    total_start_time = time.time()

    for script in test_scripts:
        result = run_single_test(script)
        all_results.append(result)
        print("-" * 50)

    total_duration = round(time.time() - total_start_time, 4)
    
    summary = {
        'total_tests': len(all_results),
        'success': sum(1 for r in all_results if r['status'] == 'success'),
        'failure': sum(1 for r in all_results if r['status'] == 'failure'),
        'timeout': sum(1 for r in all_results if r['status'] == 'timeout'),
        'error': sum(1 for r in all_results if r['status'] == 'error'),
        'total_duration_seconds': total_duration,
    }

    print("\n--- 테스트 요약 ---")
    print(f"총 테스트: {summary['total_tests']}")
    print(f"  - 성공: {summary['success']}")
    print(f"  - 실패: {summary['failure']}")
    print(f"  - 타임아웃: {summary['timeout']}")
    print(f"  - 오류: {summary['error']}")
    print(f"총 실행 시간: {summary['total_duration_seconds']}초")
    print("--- --- --- --- ---\n")

    # 결과 데이터를 JSON 파일로 저장
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(RESULTS_DIR, f'test_results_{timestamp}.json')

    final_output = {
        'summary': summary,
        'results': all_results
    }

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=4)
        print(f"결과가 다음 파일에 저장되었습니다: {output_filename}")
    except IOError as e:
        print(f"결과 파일 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
