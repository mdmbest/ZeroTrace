pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-token',
                    url: 'https://github.com/mdmbest/ZeroTrace.git'
            }
        }

        stage('Build') {
            steps {
                bat '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt || echo "Pas de requirements.txt"
                '''
            }
        }

        stage('DAST - OWASP ZAP') {
            steps {
                bat '''
                    docker run --rm -v "%CD%:/zap/wrk" --network host ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://localhost:3000 -r zap-report.html -I || exit 0
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.html', allowEmptyArchive: true
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
                    <p><b>Durée :</b> ${currentBuild.durationString}</p>
                    <p>Rapport ZAP en pièce jointe</p>
                    <a href="${BUILD_URL}">Voir le build Jenkins</a>
                """,
                mimeType: 'text/html',
                attachmentsPattern: 'zap-report.html',
                to: 'mamediarram664@gmail.com'
            )
        }
        failure {
            emailext(
                subject: "❌ ZeroTrace - ERREURS Build #${BUILD_NUMBER}",
                body: """
                    <h2>⚠️ Erreurs détectées !</h2>
                    <p>Le build #${BUILD_NUMBER} a échoué.</p>
                    <a href="${BUILD_URL}console">Voir les logs</a>
                """,
                mimeType: 'text/html',
                to: 'mamediarram664@gmail.com'
            )
        }
    }
}
