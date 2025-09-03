<script setup>
import MainLayout from '../components/MainLayout.vue'
</script>

<template>
  <MainLayout>
    <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="max-w-4xl mx-auto">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 tracking-tight">Privacy Policy</h1>
          <p class="mt-2 text-lg text-gray-600">
            Last updated: {{ new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) }}
          </p>
        </div>

        <!-- Privacy Policy Content -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 sm:p-8 lg:p-12">
          <div class="prose prose-lg max-w-none">
            
            <!-- Introduction -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
              <p class="text-gray-700 leading-relaxed mb-4">
                This Privacy Policy describes how the GDPR Compliance Tool ("we," "our," or "us") collects, uses, 
                and protects your personal information when you use our data processing and masking services. 
                We are committed to protecting your privacy and ensuring compliance with the General Data 
                Protection Regulation (GDPR) and other applicable data protection laws.
              </p>
              <p class="text-gray-700 leading-relaxed">
                By using our services, you agree to the collection and use of information in accordance 
                with this Privacy Policy.
              </p>
            </section>

            <!-- Data Collection -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">2. Information We Collect</h2>
              
              <h3 class="text-xl font-medium text-gray-900 mb-3">2.1 Personal Information</h3>
              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li><strong>Account Information:</strong> Username, password (encrypted), and role assignments</li>
                <li><strong>Contact Information:</strong> Email addresses for system notifications</li>
                <li><strong>Usage Data:</strong> Login times, file processing activities, and system interactions</li>
                <li><strong>File Metadata:</strong> File names, sizes, upload dates, and processing status</li>
              </ul>

              <h3 class="text-xl font-medium text-gray-900 mb-3">2.2 Technical Information</h3>
              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li><strong>System Logs:</strong> Error logs, processing logs, and system performance data</li>
                <li><strong>Security Data:</strong> IP addresses, browser information, and access patterns</li>
                <li><strong>Processing Data:</strong> Data masking rules, patterns, and processing configurations</li>
              </ul>
            </section>

            <!-- Data Processing -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">3. How We Use Your Information</h2>
              
              <h3 class="text-xl font-medium text-gray-900 mb-3">3.1 Legal Basis for Processing</h3>
              <p class="text-gray-700 leading-relaxed mb-4">
                We process your personal data based on the following legal grounds:
              </p>
              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li><strong>Legitimate Interest:</strong> System security, fraud prevention, and service improvement</li>
                <li><strong>Contract Performance:</strong> Providing data processing and masking services</li>
                <li><strong>Legal Obligation:</strong> Compliance with applicable laws and regulations</li>
                <li><strong>Consent:</strong> Where explicitly provided for specific processing activities</li>
              </ul>

              <h3 class="text-xl font-medium text-gray-900 mb-3">3.2 Processing Purposes</h3>
              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li>User authentication and authorization</li>
                <li>File processing and data masking operations</li>
                <li>System monitoring and performance optimization</li>
                <li>Security monitoring and threat detection</li>
                <li>Compliance reporting and audit trails</li>
                <li>Customer support and technical assistance</li>
              </ul>
            </section>

            <!-- Data Storage -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">4. Data Storage and Retention</h2>
              
              <h3 class="text-xl font-medium text-gray-900 mb-3">4.1 Storage Location</h3>
              <p class="text-gray-700 leading-relaxed mb-4">
                Your data is stored on secure servers located within the European Economic Area (EEA) 
                or in countries with adequate data protection levels as determined by the European Commission.
              </p>

              <h3 class="text-xl font-medium text-gray-900 mb-3">4.2 Retention Periods</h3>
              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li><strong>User Accounts:</strong> Retained until account deletion or 3 years of inactivity</li>
                <li><strong>File Data:</strong> Retained for 90 days after processing completion</li>
                <li><strong>System Logs:</strong> Retained for 1 year for security and compliance purposes</li>
                <li><strong>Processing Records:</strong> Retained for 7 years for audit and compliance requirements</li>
              </ul>
            </section>

            <!-- User Rights -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">5. Your Rights Under GDPR</h2>
              
              <p class="text-gray-700 leading-relaxed mb-4">
                As a data subject, you have the following rights regarding your personal data:
              </p>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h4 class="font-semibold text-gray-900 mb-2">Right of Access</h4>
                  <p class="text-sm text-gray-700">Request copies of your personal data and processing information</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h4 class="font-semibold text-gray-900 mb-2">Right to Rectification</h4>
                  <p class="text-sm text-gray-700">Correct inaccurate or incomplete personal data</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h4 class="font-semibold text-gray-900 mb-2">Right to Erasure</h4>
                  <p class="text-sm text-gray-700">Request deletion of your personal data under certain circumstances</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h4 class="font-semibold text-gray-900 mb-2">Right to Restriction</h4>
                  <p class="text-sm text-gray-700">Limit processing of your personal data</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h4 class="font-semibold text-gray-900 mb-2">Right to Portability</h4>
                  <p class="text-sm text-gray-700">Receive your data in a structured, machine-readable format</p>
                </div>
                <div class="bg-gray-50 p-4 rounded-lg">
                  <h4 class="font-semibold text-gray-900 mb-2">Right to Object</h4>
                  <p class="text-sm text-gray-700">Object to processing based on legitimate interests</p>
                </div>
              </div>

              <p class="text-gray-700 leading-relaxed">
                To exercise any of these rights, please contact us using the information provided in the 
                "Contact Us" section below. We will respond to your request within 30 days.
              </p>
            </section>

            <!-- Data Security -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">6. Data Security</h2>
              
              <p class="text-gray-700 leading-relaxed mb-4">
                We implement appropriate technical and organizational measures to protect your personal data:
              </p>

              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li><strong>Encryption:</strong> Data encrypted in transit and at rest using industry-standard protocols</li>
                <li><strong>Access Controls:</strong> Role-based access controls and multi-factor authentication</li>
                <li><strong>Network Security:</strong> Firewalls, intrusion detection, and regular security assessments</li>
                <li><strong>Data Masking:</strong> Advanced data masking techniques to protect sensitive information</li>
                <li><strong>Regular Backups:</strong> Automated backups with secure storage and recovery procedures</li>
                <li><strong>Staff Training:</strong> Regular security awareness training for all personnel</li>
              </ul>
            </section>

            <!-- Third Parties -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">7. Third-Party Services</h2>
              
              <p class="text-gray-700 leading-relaxed mb-4">
                We may use third-party services to provide our platform functionality. These services are 
                carefully selected and bound by data processing agreements to ensure GDPR compliance:
              </p>

              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li><strong>Cloud Infrastructure:</strong> Secure cloud hosting services with GDPR compliance</li>
                <li><strong>Monitoring Services:</strong> System monitoring and performance analytics</li>
                <li><strong>Security Services:</strong> Threat detection and security monitoring tools</li>
                <li><strong>Backup Services:</strong> Secure data backup and disaster recovery services</li>
              </ul>
            </section>

            <!-- Cookies -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">8. Cookies and Tracking</h2>
              
              <p class="text-gray-700 leading-relaxed mb-4">
                Our platform uses essential cookies for authentication and session management. We do not 
                use tracking cookies or third-party analytics that collect personal information.
              </p>

              <h3 class="text-xl font-medium text-gray-900 mb-3">8.1 Cookie Types</h3>
              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li><strong>Session Cookies:</strong> Essential for user authentication and session management</li>
                <li><strong>Security Cookies:</strong> CSRF protection and security token management</li>
                <li><strong>Preference Cookies:</strong> User interface preferences and settings</li>
              </ul>
            </section>

            <!-- Data Breaches -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">9. Data Breach Notification</h2>
              
              <p class="text-gray-700 leading-relaxed mb-4">
                In the event of a data breach that may result in a high risk to your rights and freedoms, 
                we will notify you and the relevant supervisory authority within 72 hours of becoming 
                aware of the breach.
              </p>

              <p class="text-gray-700 leading-relaxed">
                Our incident response procedures include immediate containment, assessment of impact, 
                notification to authorities and affected individuals, and implementation of corrective measures.
              </p>
            </section>

            <!-- Changes to Policy -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">10. Changes to This Privacy Policy</h2>
              
              <p class="text-gray-700 leading-relaxed mb-4">
                We may update this Privacy Policy from time to time to reflect changes in our practices 
                or applicable laws. We will notify you of any material changes by:
              </p>

              <ul class="list-disc pl-6 text-gray-700 mb-4 space-y-2">
                <li>Posting the updated policy on our website</li>
                <li>Sending email notifications to registered users</li>
                <li>Displaying a notice on the platform login page</li>
              </ul>

              <p class="text-gray-700 leading-relaxed">
                Your continued use of our services after any changes constitutes acceptance of the updated policy.
              </p>
            </section>

            <!-- Contact Information -->
            <section class="mb-8">
              <h2 class="text-2xl font-semibold text-gray-900 mb-4">11. Contact Us</h2>
              
              <p class="text-gray-700 leading-relaxed mb-4">
                If you have any questions about this Privacy Policy or wish to exercise your rights, 
                please contact us:
              </p>

              <div class="bg-indigo-50 p-6 rounded-lg">
                <h3 class="text-lg font-semibold text-gray-900 mb-3">Data Protection Officer</h3>
                <div class="space-y-2 text-gray-700">
                  <p><strong>Email:</strong> privacy@gdpr-tool.com</p>
                  <p><strong>Phone:</strong> +1 (555) 123-4567</p>
                  <p><strong>Address:</strong></p>
                  <p class="ml-4">
                    GDPR Compliance Tool<br>
                    Data Protection Office<br>
                    123 Privacy Street<br>
                    Data City, DC 12345<br>
                    United States
                  </p>
                </div>
              </div>

              <div class="mt-6 bg-yellow-50 p-6 rounded-lg">
                <h3 class="text-lg font-semibold text-gray-900 mb-3">Supervisory Authority</h3>
                <p class="text-gray-700 mb-2">
                  You also have the right to lodge a complaint with your local data protection authority 
                  if you believe we have not handled your personal data in accordance with applicable law.
                </p>
                <p class="text-sm text-gray-600">
                  For EU residents, you can find your local supervisory authority at: 
                  <a href="https://edpb.europa.eu/about-edpb/board/members_en" 
                     class="text-indigo-600 hover:text-indigo-700 underline" 
                     target="_blank" 
                     rel="noopener noreferrer">
                    European Data Protection Board
                  </a>
                </p>
              </div>
            </section>

          </div>
        </div>

        <!-- Footer -->
        <footer class="mt-12 text-center text-sm text-gray-500">
          <p>© {{ new Date().getFullYear() }} GDPR Compliance Tool. All rights reserved.</p>
          <p class="mt-2">
            This privacy policy is designed to comply with GDPR, CCPA, and other applicable data protection regulations.
          </p>
        </footer>
      </div>
    </div>
  </MainLayout>
</template>

