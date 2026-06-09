pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/mdmbest/ZeroTrace.git'
            }
        }

        stage('Build') {
            steps {
                bat '''
                    "C:\\Users\\HP\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe" -m pip install --upgrade pip || echo "skipped"
                    "C:\\Users\\HP\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe" -m pip install -r requirements.txt || echo "Pas de requirements.txt"
                '''
            }
        }

        stage('SAST - Semgrep') {
            steps {
                bat '''
                    "C:\\Users\\HP\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe" -m semgrep --config auto --json -o semgrep-report.json --include="*.py" . || exit 0
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'semgrep-report.json', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            emailext(
                subject: "ZeroTrace Build #${BUILD_NUMBER} - ${currentBuild.currentResult}",
                body: """
                    <h2>Rapport DevSecOps - ZeroTrace</h2>
                    <p><b>Statut :</b> ${currentBuild.currentResult}</p>
                    <p><b>Build :</b> #${BUILD_NUMBER}</p>
                    <p><b>Duree :</b> ${currentBuild.durationString}</p>
                    <p>Rapport Semgrep en piece jointe</p>
                    <a href="${BUILD_URL}">Voir le build Jenkins</a>
                """,
                mimeType: 'text/html',
                attachmentsPattern: 'semgrep-report.json',
                to: 'mamediarram664@gmail.com'
            )
        }
        failure {
            emailext(
                subject: "ZeroTrace - ERREURS Build #${BUILD_NUMBER}",
                body: """
                    <h2>Erreurs detectees !</h2>
                    <p>Le build #${BUILD_NUMBER} a echoue.</p>
                    <a href="${BUILD_URL}console">Voir les logs</a>
                """,
                mimeType: 'text/html',
                to: 'mamediarram664@gmail.com'
            )
        }
    }
}
